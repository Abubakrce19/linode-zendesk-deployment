import json
import os
import re 
import requests
from retry import retry
import pandas as pd
from sentence_transformers.util import semantic_search
import torch
from datasets import load_dataset
import zenpy
import datetime
import json 
from django.conf import settings
import textwrap
from zenpy import Zenpy


model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = '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' # settings.HF_TOKEN
api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}
EDEN_AI_API_KEY = settings.EDEN_AI_API_KEY

print()
# Calling GPT APIs
def generate_gpt(text, history=[]):
        headers = {"Authorization": f"Bearer {EDEN_AI_API_KEY}"}
        url ="https://api.edenai.run/v2/text/chat"
        payload = {
            "providers": "openai",
            "text": text,
            "chat_global_action": "Follow user instructions",
            "previous_history" : history,
            "temperature" : 0.0,
            "settings":{"openai":"gpt-3.5-turbo"},
            "max_tokens" : 1000
            }
        response = requests.post(url, json=payload, headers=headers)
        try:
            result = json.loads(response.text)
            msg = result['openai']['generated_text']
            # print(msg)
        except Exception as e:
            return 
        return msg
    

@retry(tries=3, delay=10)
def query(texts):
    response = requests.post(api_url, headers=headers, json={"inputs": texts})
    result = response.json()
    if isinstance(result, list):
      return result
    elif list(result.keys())[0] == "error":
      raise RuntimeError(
          "The model is currently loading, please re-run the query."
          )

def save_list_to_file(lst, filename):
    with open(filename, 'w') as file:
        for item in lst:
            file.write(str(item) + '\n')

def load_list_from_file(filename):
    lst = []
    with open(filename, 'r') as file:
        for line in file:
            lst.append(line.strip())
    return lst

# ============ Functions ============


# Get all the tickets to build embeddings 
def get_tickets(creds):
    tickets = []
    if creds is not None:
        zenpy_client = Zenpy(**creds)

        for i, ticket in enumerate(zenpy_client.search(type='ticket')):
            ticket_info = ""

            try:
                ticket_info += f"Ticket ID: {ticket.id}\n"
                ticket_info += f"Ticket Description: {ticket.description}\n"
                ticket_info += f"Ticket Subject: {ticket.subject}\n"
                ticket_info += f"Ticket {ticket.id} URL: {ticket.url}\n"
                ticket_info += f"Ticket Status: {ticket.status}\n"
                ticket_info += f"Assignee Name: {ticket.assignee_name}\n"
            except AttributeError:
                ticket_info += f"Ticket ID: Not available\n"
                ticket.id = f"Ticket Unknown {i}"
                ticket_info += f"Ticket Description: Not available\n"
                ticket_info += f"Ticket Subject: Not available\n"
                ticket_info += f"Ticket URL: Not available\n"
                ticket_info += f"Ticket Status: Not available\n"
                ticket_info += f"Assignee Name: Not available\n"

            tickets.append(ticket_info)
    return tickets


# build embeddings 
def build_embeddings(creds, _id):
  txt_list = get_tickets(creds)
  output = query(txt_list)
  csv_ = str(_id) + '.csv'
  save_list_to_file(txt_list, str(_id) + '.txt')

  embeddings = pd.DataFrame(output)
  embeddings.to_csv(csv_, index=False)
  print("Embeddings saved to disk...")


# semantic search over the database 
def search_query(text, _id):
  csv_ = str(_id) + '.csv'
  txt_list = load_list_from_file(str(_id) + '.txt')
  pdf_index = load_dataset("csv", data_files = csv_)
  embeddings = torch.from_numpy(pdf_index["train"].to_pandas().to_numpy()).to(torch.float)
  question = [text]
  query_embeddings = torch.FloatTensor(query(question))

  hits = semantic_search(query_embeddings, embeddings, top_k=3)
  results = [txt_list[hits[0][i]['corpus_id']] for i in range(len(hits[0]))]

  _res = "\n\n".join(results)
  if len(_res) > 9000:
    _res = _res[:9000]
  return _res


# retrive the tciket by id 
def get_ticket_by_id(creds, ticket_id):
    zenpy_client = Zenpy(**creds)
    try:
        # Retrieve the ticket by ID
        ticket = zenpy_client.tickets(id=ticket_id)

        # Format the ticket details
        ticket_details = f"Ticket ID: {ticket.id}\n"
        ticket_details += f"Ticket Description: {ticket.description}\n"
        ticket_details += f"Ticket Subject: {ticket.subject}\n"
        ticket_details += f"Ticket {ticket.id} URL: {ticket.url}\n"
        ticket_details += f"Ticket Status: {ticket.status}\n"

        return ticket_details
    except zenpy.lib.exception.APIException as e:
        # Handle any API exceptions
        print(f"An error occurred: {e}")


# Mapping start_dates & end_dates to specific month 
def get_month_dates(month_name):
    # Get the current year
    current_year = datetime.datetime.now().year

    # Map month names to their corresponding numbers
    month_mapping = {
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }

    # Convert the month name to lowercase for case-insensitive matching
    month_name = month_name.lower()

    # Check if the provided month name is valid
    if month_name not in month_mapping:
        return None, None

    # Get the corresponding month number
    month_number = month_mapping[month_name]

    # Set the start and end dates for the specified month
    start_date = datetime.datetime(current_year, month_number, 1)
    end_date = datetime.datetime(current_year, month_number + 1, 1)
    return start_date, end_date


# retrive the tickets based on time period 
def get_ticket_by_time_period(creds, month_name):
    zenpy_client = Zenpy(**creds)
    try:
        start_date, end_date = get_month_dates(month_name)

        if start_date is None:
            return None

        tickets = zenpy_client.search(
            type='ticket',
            created_between=(start_date, end_date),
            query="created>{}".format(start_date.strftime('%Y-%m-%d'))
        )
        # Format the ticket details
        ticket_details = ""
        for ticket in tickets:
            ticket_details += f"Ticket ID: {ticket.id}\n"
            ticket_details += f"Ticket Description: {ticket.description}\n"
            ticket_details += f"Ticket Subject: {ticket.subject}\n"
            ticket_details += f"Ticket {ticket.id} URL: {ticket.url}\n"
            ticket_details += f"Ticket Status: {ticket.status}\n\n"

        return ticket_details
    except Exception as e:
        # Handle any API exceptions
        print(f"An error occurred: {e}")


# retrive the tickets based on assignee_name 
def get_tickets_by_agent(creds, assignee_name):
    zenpy_client = Zenpy(**creds)
    try:
        # Retrieve the tickets assigned to the specific agent
        tickets = zenpy_client.search(type='ticket', assignee=assignee_name)

        # Format the ticket details
        ticket_details = ""
        for ticket in tickets:
            ticket_details += f"Ticket ID: {ticket.id}\n"
            ticket_details += f"Ticket Description: {ticket.description}\n"
            ticket_details += f"Ticket Subject: {ticket.subject}\n"
            ticket_details += f"Ticket {ticket.id} URL: {ticket.url}\n"
            ticket_details += f"Ticket Status: {ticket.status}\n\n"

        return ticket_details
    except zenpy.lib.exception.APIException as e:
        # Handle any API exceptions
        print(f"An error occurred: {e}")


# retrive the tickets based on assignee_name & time_period
def get_tickets_by_agent_in_period(creds, assignee_name, month_name):
    zenpy_client = Zenpy(**creds)
    try:
        start_date, end_date = get_month_dates(month_name)

        if start_date is None:
            return None
        
        tickets = zenpy_client.search(
            type='ticket',
            created_between=(start_date, end_date),
            query="created>{}".format(start_date.strftime('%Y-%m-%d'))
        )
        # Format the ticket details
        ticket_details = ""
        for ticket in tickets:
            ticket_details += f"Ticket ID: {ticket.id}\n"
            ticket_details += f"Ticket Description: {ticket.description}\n"
            ticket_details += f"Ticket Subject: {ticket.subject}\n"
            ticket_details += f"Ticket {ticket.id} URL: {ticket.url}\n"
            ticket_details += f"Ticket Status: {ticket.status}\n\n"

        return ticket_details
    except Exception as e:
        # Handle any API exceptions
        print(f"An error occurred: {e}")


# Simple base prompt 
BASE_PROMPT = '''
Answer questions and output in well formatted manner.

Question:
'''

# Prompt that classify query to structured format 
MASTER_PROMPT = '''
Act as a Tickets AI agent. You will be given a query and based on which you need to output certain processings in a JSON format. Your output should be only in JSON, no greetings text or replies or explanations required. IT IS IMPORTANT TO OUTPUT ONLY IN JSON FORMAT.
Format:
{
    "is_ticket_by_id": 'Should only be integer. Write ticket id if query is asking a operation for a particular/specific ticket by id else if not then write false',
    "tickets_in_timeperiod": 'Should only be NAME of month. Write only the name of the Months, if query is asking for tickets that belongs to a specific timeperiod then write its closest month, DO NOT WRITE ANYTHING EXCEPT NAME OF THE MONTH else write false',
    "tickets_by_agent": 'Should only be name of assignee/agent. Write the name of the agent if query is asking a operation by certain agents or customer support tickets else write false',
    "tickets_by_agent_in_period": 'Should only be name of agent,month name. Write the name of the agent along with the name of the month like (agent 1, february) separated by a comma (,) if query is asking a operation by certain agent in relation with time period (DO NOT WRITE ANYTHING EXCEPT NAME OF THE AGENT,MONTH) else write false',
}

PROPERLY WRITE THE KEYS IN JSON FORMAT WITH VALID JSON OUTPUT.
ONLY OUTPUT IN JSON FORMAT. 
Query: 
'''


# Main pipeline that query based on user questions 
def main_pipeline(creds, _query_txt, _id):
    print(_query_txt)
    output = generate_gpt(MASTER_PROMPT + _query_txt , history=[])
    print(output)
    final_output = ''

    try:
        output_json = json.loads(output)
    except Exception as e:
        output_json = json.loads(output)


    if output_json['is_ticket_by_id'] != False:
        _r = get_ticket_by_id(creds, output_json['is_ticket_by_id'])
        if len(_r) > 9000:
            final_output = ""
            chunks = textwrap.wrap(_r, 8000)
            for i in chunks:
                final_output += generate_gpt(BASE_PROMPT + _query_txt + ' Tickets context: ' + i , history=[])
        else:
            final_output = generate_gpt(BASE_PROMPT + _query_txt + ' Tickets context: ' + _r , history=[])

    elif output_json['tickets_in_timeperiod'] != False:
        _month = output_json['tickets_in_timeperiod']
        print(_month)
        _r = get_ticket_by_time_period(creds, str(_month))
        if _r is None:
            final_output = "Only supports the name of the specific month"

        if len(_r) > 9000:
            final_output = ""
            chunks = textwrap.wrap(_r, 8000)
            for i in chunks:
                final_output += generate_gpt(BASE_PROMPT + _query_txt + ' These are the all tickets ' + i , history=[])
        else:
            print(_r)
            final_output = generate_gpt(BASE_PROMPT + _query_txt + "Tickets " + _r , history=[])

    elif output_json['tickets_by_agent'] != False:
        _name = output_json['tickets_by_agent']
        print( _name)
        _r = get_tickets_by_agent(creds, _name)
        if len(_r) > 9000:
            final_output = ""
            chunks = textwrap.wrap(_r, 8000)
            for i in chunks:
                final_output += generate_gpt(BASE_PROMPT + _query_txt + ' These are the all tickets ' + i , history=[])
        else:
            final_output = generate_gpt(BASE_PROMPT + _query_txt + "These are the all tickets " + _r , history=[])

    elif output_json['tickets_by_agent_in_period'] != False:
        _name = output_json['tickets_by_agent_in_period'].split(',')[0]
        _month = output_json['tickets_by_agent_in_period'].split(',')[1]
        print( _name, _month)

        _r = get_tickets_by_agent_in_period(creds, _name, _month)
        if len(_r) > 9000:
            final_output = ""
            chunks = textwrap.wrap(_r, 8000)
            for i in chunks:
                final_output += generate_gpt(BASE_PROMPT + _query_txt + ' These are the all tickets ' + i , history=[])
        else:
            final_output = generate_gpt(BASE_PROMPT + _query_txt + "These are the all tickets " + _r , history=[])

    else:
        result = search_query(_query_txt, _id)
        if len(result) > 9000:
            final_output = ""
            chunks = textwrap.wrap(result, 8000)
            for i in chunks:
                final_output += generate_gpt(BASE_PROMPT + _query_txt + ' These are the all tickets ' + i , history=[])
        else:
            final_output = generate_gpt(BASE_PROMPT + _query_txt + "These are the all tickets " + result , history=[])

    return final_output



# creds = {
# 'email' : "abhi22@skiff.com",
# 'token' : 'PvrVLyjWWagOP0EeHA8RZeaZxwmdzi9rP0S3yGOr',
# 'subdomain': 'skiff5911'
# }

# print(get_ticket_by_time_period(creds, 'august'))