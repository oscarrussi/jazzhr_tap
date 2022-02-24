import os, sys
sys.path.insert(0, os.getcwd()) 
import singer
from jazzhr_resources.http_request import call_api
from jazzhr_resources.load_jsons import load_schema


def main():
  schema = load_schema("files")
  current_applicant = None

  endpoint = "https://api.resumatorapi.com/v1/"

  def retrieve_applicants_per_page(page):
    authenticated_endpoint = f"{endpoint}applicants/page/{page}"
    api_response = call_api(authenticated_endpoint)
    if not isinstance(api_response, list):
      api_response = [api_response]
    return [r["id"] for r in api_response]

  def retrieve_files_per_page(page):
    authenticated_endpoint = f"{endpoint}files/applicant_id/{current_applicant}/page/{page}"
    api_response = call_api(authenticated_endpoint)
    if not isinstance(api_response, list):
      api_response = [api_response]
    return api_response

  def retrieve_all_items(retrieve_method):
    items = []
    pursue = True
    page = 1
    while pursue:
      response = retrieve_method(page)
      items = items + response
      page = page + 1
      if len(response) < 100:
        pursue = False
    return items

  applicants = list(set(retrieve_all_items(retrieve_applicants_per_page)))
  all_files = []

  for a in applicants:
    current_applicant = a
    all_files = all_files + retrieve_all_items(retrieve_files_per_page)

  stream = "jazzhr_files"

  singer.write_schema(stream_name=stream, schema=schema, key_properties=["id"])

  for file in all_files:
    file["file_size"] = int(file["file_size"])
    singer.write_record(stream_name=stream,
                        record=file)


if __name__ == "__main__":
  main()
