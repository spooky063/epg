#!/usr/bin/env python3
import xmltodict
import json
import subprocess
import sys
import urllib.request
import gzip
import shutil
import os

def download_and_extract(url, output_file):
    print(f"📥 Téléchargement depuis: {url}")

    try:
        temp_file = "temp_download"
        urllib.request.urlretrieve(url, temp_file)
        print(f"✓ Téléchargement terminé")

        if url.endswith('.gz'):
            print(f"📦 Décompression du fichier .gz...")
            with gzip.open(temp_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(temp_file)
            print(f"✓ Décompression terminée: {output_file}")
        else:
            shutil.move(temp_file, output_file)
            print(f"✓ Fichier sauvegardé: {output_file}")

        return output_file
    except urllib.error.URLError as e:
        print(f"✗ Erreur lors du téléchargement: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur: {e}")
        sys.exit(1)

def xml_to_json(xml_file, json_file):
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    data_dict = xmltodict.parse(xml_content)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)

    print(f"✓ Conversion XML→JSON terminée: {json_file}")
    return json_file

def create_jq_filter(filter_file):
    jq_filter = '''# Liste des channels à filtrer
["TF1.fr", "France2.fr", "France3.fr", "France4.fr"] as $channelsFilter |

{
  channels: (
    .tv.channel
    | if type == "array" then . else [.] end
    | map(select(.["@id"] as $id | $channelsFilter | contains([$id])))
    | to_entries
    | map(
        {
          sourceId: (.key + 1),
          id: .value["@id"],
          name: (
            if .value["display-name"] | type == "object" then
              .value["display-name"]["#text"]
            else
              .value["display-name"]
            end
          ),
          icon: (
            if .value.icon then
              (if .value.icon | type == "object" then
                .value.icon["@src"]
              else
                null
              end)
            else
              null
            end
          )
        }
      )
  ),
  programs: (
    .tv.programme
    | if type == "array" then . else [.] end
    | map(select(.["@channel"] as $ch | $channelsFilter | contains([$ch])))
    | map(
        {
          title: (
            if .title | type == "array" then
              (.title | map(select(.["@lang"] == "fr")) | first // .title[0] | .["#text"])
            elif .title | type == "object" then
              .title["#text"]
            else
              .title
            end
          ),
          subTitle: (
            if .["sub-title"] | type == "object" then
              .["sub-title"]["#text"]
            else
              .["sub-title"]
            end
          ),
          start: .["@start"],
          stop: .["@stop"],
          channel: .["@channel"],
          description: (
            if .desc | type == "object" then
              .desc["#text"]
            else
              .desc
            end
          ),
          categories: (
            if .category then
              (if .category | type == "array" then
                .category | map(if type == "object" then .["#text"] else . end)
              else
                [if .category | type == "object" then .category["#text"] else .category end]
              end)
            else
              null
            end
          ),
          credits: (
            if .credits then
                .credits
            else
                null
            end
          ),
          year: (
            if .date then
              (.date | tostring | .[0:4] | tonumber)
            else
              null
            end
          ),
          country: (
            if .country | type == "object" then
              .country["#text"]
            else
              .country
            end
          ),
          icon: (
            if .icon then
              (if .icon | type == "object" then
                .icon["@src"]
              else
                null
              end)
            else
              null
            end
          ),
          episodeSeason: (
            if .["episode-num"] then
              (if .["episode-num"] | type == "object" then
                (.["episode-num"]["#text"] // "" | split(".")[0] | if . == "" then null else (tonumber + 1) end)
              else
                null
              end)
            else
              null
            end
          ),
          episodeNumber: (
            if .["episode-num"] then
              (if .["episode-num"] | type == "object" then
                (.["episode-num"]["#text"] // "" | split(".")[1] // "" | if . == "" then null else (tonumber + 1) end)
              else
                null
              end)
            else
              null
            end
          ),
          rating: (
            if .rating then
              [{
                system: (.rating["@system"] // null),
                value: (
                  if .rating.value | type == "object" then
                    .rating.value["#text"]
                  else
                    .rating.value
                  end
                ),
                icon: (
                  if .rating.icon then
                    (if .rating.icon | type == "object" then
                      .rating.icon["@src"]
                    else
                      null
                    end)
                  else
                    null
                  end
                )
              }]
            else
              null
            end
          )
        }
      )
    | group_by(.channel)
    | map({key: .[0].channel, value: .})
    | from_entries
  )
}
'''

    with open(filter_file, 'w', encoding='utf-8') as f:
        f.write(jq_filter)

    print(f"✓ Filtre jq créé: {filter_file}")

def apply_jq_filter(input_json, output_json, jq_filter_file):
    try:
        with open(jq_filter_file, 'r', encoding='utf-8') as f:
            jq_filter = f.read()

        result = subprocess.run(
            ['jq', '-f', jq_filter_file, input_json],
            capture_output=True,
            text=True,
            check=True
        )

        with open(output_json, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

        print(f"✓ Filtrage jq terminé: {output_json}")

    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur jq: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Erreur: jq n'est pas installé. Installez-le avec: apt install jq (Linux) ou brew install jq (Mac)")
        sys.exit(1)

def delete_temporary_files(*files):
    print(f"🧹 Nettoyage des fichiers intermédiaires...")

    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  ✓ Supprimé: {file}")
            except Exception as e:
                print(f"  ⚠ Impossible de supprimer {file}: {e}")
        else:
            print(f"  ⓘ Fichier inexistant: {file}")

if __name__ == "__main__":
    xml_source = None
    xml_file = "output.xml"
    intermediate_json = "intermediate.json"
    jq_filter_file = "filter.jq"
    output_json = "output.json"

    if len(sys.argv) > 1:
        xml_source = sys.argv[1]
    else:
        print("Usage: python app.py <source_url_or_file> [output.json]")
        print("Exemple: python app.py https://xmltvfr.fr/xmltv/xmltv_tnt.xml.gz")
        print("Exemple: python app.py input.xml output.json")
        sys.exit(1)

    if len(sys.argv) > 2:
        output_json = sys.argv[2]

    try:
        if xml_source.startswith('http://') or xml_source.startswith('https://'):
            xml_file = download_and_extract(xml_source, xml_file)
        else:
            if xml_source.endswith('.gz'):
                print(f"📦 Décompression du fichier local .gz...")
                with gzip.open(xml_source, 'rb') as f_in:
                    with open(xml_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"✓ Décompression terminée: {xml_file}")
            else:
                xml_file = xml_source

        xml_to_json(xml_file, intermediate_json)

        create_jq_filter(jq_filter_file)

        apply_jq_filter(intermediate_json, output_json, jq_filter_file)

        delete_temporary_files(xml_file, intermediate_json, jq_filter_file)

        print(f"\n✓ Transformation terminée vers: {output_json}")
    except FileNotFoundError as e:
        print(f"✗ Erreur: Fichier non trouvé - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur: {e}")
        sys.exit(1)