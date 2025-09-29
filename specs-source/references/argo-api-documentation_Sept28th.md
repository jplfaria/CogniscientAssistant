I can provide the entire content formatted as Markdown text here, which you can then copy and save as a `.md` file on your computer. Here is the full document converted into Markdown format:

---

# Argo API Documentation

_Last updated: September 28, 2025 (mtd)_

## Introduction

The Argo Gateway API provides centralized, consistent, and data-secure programmable access to multiple Large Language Models (LLMs) available exclusively for internal users and applications at Argonne. Through a straightforward “LLM-as-a-service” interface, we can better facilitate scientific research, enable advanced operational integrations, and lower the barriers to entry of leveraging LLMs within the national laboratory regulatory ecosystem while simplifying the usage, management, maintenance, and transparency of generative AI across the lab.

The gateway API for Argo is currently available as a stable release in our production environment (“prod”). This release contains all recent features, including:

1. Ability to pass the full “messages” object with turn-by-turn conversation elements,
2. All available OpenAI LLM inference and embedding models,
3. Additional error handling and reporting of incorrect call structures and values,
4. A new API docs interface for testing individual calls.

We will continue to develop new features within our development environments (“dev”, “test”) that will include the latest features and enhancements implemented for testing before releasing to prod. We now strongly recommend switching your existing calls to the production environment and no longer routinely use dev or test, unless you are helping evaluate new functionality.

Please refer to the table of contents on the right side of this document for navigation → → →

---

### Argo Gateway API deployed to production!

All latest stable features are now available in production.

Update your endpoints to:

- `https://apps.inside.anl.gov/argoapi/api/v1/resource/chat/`
- `https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/`

API explore web interface (Swagger UI):  
  
Test your API calls from your browser.

**IMPORTANT:** All API calls should include your ANL domain name. Please use your ANL domain name in the “user” field of your Argo calls. If you would like to create a service account to represent an application calling Argo, please reach out to mdearing@anl.gov for instructions.

In the near future, we will be adding authentication to make sure that the username included in the Argo API call is valid.

---

## What’s New!

- **NEW! Claude Opus 4.1 model is now available.** See details below. If you are using a local host with argo-proxy, simply restart your host and the Claude Opus 4.1 model will be available. No library upgrade required. If you are vibe coding with Continue.dev (with Argo), the config file template has been updated to include Claude Opus 4.1. Grab the update .

- **COMING SOON - Tool / Function Calling with OpenAI, Google, and Anthropic models.** If you are interested in helping test the new feature (and help work out any bugs) before we release to all users, please reach out to mdearing@anl.gov. Thank you!

---

## Prior Updates

- **OpenAI GPT-5 model suite now available.** See details below. If you are using a local host with argo-proxy, simply restart your host and the GPT-5 models will be available. No library upgrade required. If you are vibe coding with Continue.dev, the config file template has been updated to include GPT-5. Grab the update .

- **Ready for testing/feedback: Streaming endpoint**  
Now available for testing and use in the API apps-dev environment, we have a separate endpoint to return streaming responses through the Argo Gateway API:  
`https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/streamchat/`

The streaming endpoint is now working for all OpenAI, Google, and Anthropic models.

A Python testing script is available as a starting point here: `argoapi_streamchat_test.py`  
Please note that the `httpx` library is used to enable streaming and the `requests` library does not support this feature.

If you want to take a look at some interesting metadata of the streaming text returned from the LLMs, then you can use this testing script: `argoapi_streamchat_metadata_test.py`

Please test and feedback: A few more error handling needs to still be included and I welcome your feedback ASAP. As soon as we feel this endpoint is stable, then we can push it through to production. Post your testing results/experience in the Teams Argo API CoP or email mdearing@anl.gov. Thank you!

- **More OpenAI models are here!**  
These latest models are available for use in the API apps-dev environment for testing (apps-dev).  
Model IDs: gpto3 | gpto4mini | gpt41 | gpt41mini | gpt41nano

- **Google Gemini and Anthropic Claude models are here!**  
These latest models are available for use in the API apps-dev environment for testing (apps-dev). There are many new features and opportunities to leverage with these models, which will have to be added in the near future. Initially, we have these accessible for text-only via the `/chat/` (non-streaming) endpoint. There are also some different configuration requirements and options compared to OpenAI models, so additional review is necessary to understand how to best interact with all models from across multiple vendors.  
Model IDs: gemini25pro | gemini25flash | claudeopus4 | claudesonnet4 | claudesonnet37 | claudesonnet35v2

- **Want to Vibe Code with Argo?**  
Check out the new instructions documentation:  
 — please let Matthew Dearing know what you think and share any edits/suggestions. Thank you!

- **Continue, Cline, aider, Void IDE**  
  + The o1 model is now available for use in the API apps-dev environment for testing (apps-dev). Please note that the prompting structure allows for separate “system” and “user” prompts. However, all o-series reasoning models do not accept “temperature” and “top_p” and require “max_completion_tokens” instead of “max_tokens”. (Read more)  
  + The latest snapshot of GPT-4o (“2024-11-20”) model is now available for use in the API apps-dev environment for testing (apps-dev). Please use the model name: `gpt4olatest`. And, no joke, this model likes to use emojis. :-)  
  + The o3-mini model is now available for use in the API apps-dev environment for testing (apps-dev). Please note that the prompting structure allows for separate “system” and “user” prompts. However, it does not accept “temperature” and “top_p” and requires “max_completion_tokens” instead of “max_tokens”.  
  + The o1-mini model is now available for use in the API apps-dev environment for testing (apps-dev). Please note that the prompting structure is similar to o1-preview, specifically in that the model does not accept the “system” prompt.

---

## Getting started and connected

Quick Starts are available below in the ‘Example & Code Template’ sections for the Chat Completion and Embedding endpoint.

**Recommendation:** If you do not have a local Python development environment already configured, then we recommend downloading and installing Postman (free for individual use) as the most straightforward way to test calling the Argo Gateway API. Or, you may use the Argo API test docs UI at:  
DEV:   
PROD: 

---

## Usage request (general users):

At this time, you are welcome to leverage the Argo Gateway API for your Argonne-focused LLM-as-a-service needs.

Because each call to Argo incurs a small cost per prompt and per response with GPT-3.5, GPT-4, GPT-4o, GPT o1-preview, and all text embedding models, we ask that any large or long-term, automated runs are first reviewed and coordinated with Matthew Dearing, mdearing@anl.gov, for awareness.

For large (and expensive) runs, we can work with you and your division to configure an existing funded project pay for any high-volume use of the GPT models through Argo. Please reach out to Matthew Dearing (mdearing@anl.gov) for more information. Your cooperation will help with transparency of early user while we continue to develop this service and help ensure funds are available to support your needs.

---

## Usage request (within CELS):

We have a separate collection of the same GPT LLMs for exclusive use by Argo users within CELS. If you are an Argo Gateway API user working on a CELS-funded project, then you now have the option to utilize the OpenAI models that are financially supported by CELS.

**Current process:**  
To use the CELS-funded models in your API calls, you first need to be included in a special user role that will enable your access.

This role-based user feature allows you to set the “user” field to your ANL domain name or a service account to gain access the CELS-specific OpenAI models.

**Action:** If you are a user of the CELS Argo LLM models, then please email:  
Craig Stacey (stace@anl.gov) and Anthony Avarca (aavarca@anl.gov) to be included in this role.

---

## Technical Questions

For technical questions, please contact Matthew Dearing (mdearing@anl.gov)

We have an Argo API CoP group on Teams — please let Matthew know if you would like to join this channel to contribute to the continued development and use cases of the Argo Gateway API. You will have notifications of the latest updates and direct access for questions and discussions related to the use of the Argo Gateway API.

---

## Enhancement Requests

To request an enhancement, please use Vector to ‘Make a Request’ and select the ‘Argonne Application Enhancement’ item. On the form, enter “Argo Gateway API Prod” as the Application Service Name.

---

## Special Networking Connection Needs

The machine or server making the API calls to Argo must be connected to Argonne internal network or through VPN on an Argonne-managed computer if you are working off-site.

If your internal Argonne machine does not have access to the apps.inside.anl.gov domain space, then a firewall conduit can be configured to enable access from your local IP address to the Argo Gateway API.

To request this firewall conduit, please submit a Vector ticket here:

- Description: “Need access to the Argo Gateway API endpoints.”  
- Object Group Information: Select "BIS_Argo_Access" from the drop-down menu  
- Object-Group Additions: Click [Add] button  
- Pop-up window: IP Address or Network: Enter IP address. Repeat the process to add more than one IP address.

---

## Feature Listing

- Exponential backoff is included to support concurrent response during high-volume use and alleviate bottlenecks if we experience token count limits by the LLM hosting service (Azure).
- Informative error handling for incorrect API calls details or structure.
- Two ways to prompt:  
  1. Pass the complete “messages” object  
  2. Individual “system” and “prompt” (user) fields  
- … (TODO: fill out this list)

---

## Coming soon

The current token count rate for cumulative incoming requests is set at 240,000 tokens per minute. This rate is dynamically increased as resources are available within the Azure instance that hosts the selected LLM.

We expect to be able to request higher rates in the future — but this limit is what we have today.

To alleviate code crashes (or what appear to be timeouts) when this limit is reached during high volume API call routines, we will implement an exponential backoff process that will briefly pause your next request until the one-minute timing is reset.

This will eliminate the need for users to manage this server error responses and should allow for fairness in the pausing of requests when multiple users are calling the API simultaneously.

---

## Argo Community Developer Code Share

We have a DOE-hosted GitLab repository (offered through DOE CODE) to curate our Argonne community development of Argo-related codes and tools, such as a proxy to make Argo compatible with OpenAI calls.

This repository is public so anyone here can clone tools for use within your Argonne-related work.



If you are interested in contributing your code (everyone is welcome!), please email Matthew Dearing (mdearing@anl.gov).

A quick registration process required with DOE CODE to give you contributor access, and then we will set up a new project for you to push your code.

Detailed instructions for this process are available here.

---

## Endpoint: Chat Completion

POST to (PROD environment)  
`https://apps.inside.anl.gov/argoapi/api/v1/resource/chat/`  

or POST to (TEST environment)  
`https://apps-test.inside.anl.gov/argoapi/api/v1/resource/chat/`  

or POST to (DEV environment)  
`https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/`

### Structure of the API Call Object

Required: Please include your personal Argonne domain account user name or a service account in the “user” field. This value is logged so we can track usage at the Division level. If you created a service account to represent calls from an application, then this name may be included in the “user” field instead.

#### Option 1: Messages Object

Sample Python script: 
```json
{
  "user": "<your ANL domain user, e.g., mdearing>",
  "model": "<required, input a valid name>",
  "messages": [
    {"role": "system",
      "content": "You are a large language model with the name Argo"},
    {"role": "user",
      "content": "What is your name?"},
    {"role": "assistant",
      "content": "My name is Argo."},
    {"role": "user", 
      "content": "What are you?"}
  ],
  "stop": [],
  "temperature": 0.1,
  "top_p": 0.9
}
```

*Important for o1-preview and o1-mini:*  
This LLM model only accepts the `{“role”: “user”, “content”: “<your prompt>”}` dictionary in the messages object. The “system”, “temperature”, “top_p”, and “max_tokens” field values will be ignored.

#### Option 2: Singular System + prompt

Sample Python script: [argoapi_chat_test.py]
```json
{
  "user": "<your ANL domain user, e.g., mdearing>",
  "model": "<required, input a valid name>",
  "system": "<NULL, or e.g., You are a large language model with the name Argo",
  "prompt": ["what is your name?"],
  "stop": [],
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 1000,
  "max_completion_tokens": 1000
}
```

*Important for o1-preview and o1-mini:*  
This LLM model only accepts the `"prompt": ["<your prompt>"]` field. The “system”, “temperature”, “top_p”, and “max_tokens” field values will be ignored.

---

## Valid LLM Model Names

Streaming and tool/function calling is available in all models unless specified. The “model” field must include one of the following strings (to replace `<required, input a selection>` in the same calls above):

### OpenAI

| Model ID       | Max Token Input | Max Token Output | Training Data           | Notes                                                                                  |
|----------------|-----------------|------------------|------------------------|----------------------------------------------------------------------------------------|
| gpt35          | 4,096           | -                | Up to Sept 2021        | GPT-3.5 Turbo                                                                          |
| gpt35large     | 16,384          | -                | Up to Sept 2021        | GPT-3.5 Turbo 16k                                                                      |
| gpt4large      | 8,192           | -                | Up to Sept 2021        | GPT-4                                                                                  |
| gpt4turbo      | 128,000         | 4,096            | Up to Dec 2023         | GPT-4 Turbo; slower response                                                           |
| gpt4o          | 128,000         | 16,384           | Up to Oct 2023         | Text-based interactions only                                                          |
| gpt4olatest    | 128,000         | 16,384           | Up to Oct 2023         | Text-based interactions only; dev only                                                |
| gpto1preview   | 128,000         | 32,768           | Up to Oct 2023         | To be retired July 27, 2025; no tools/function calling; only user prompt and max_completion_tokens accepted |
| gpto1mini      | 128,000         | 65,536           | Up to Oct 2023         | Does not accept system role; no tools/function calling                                |
| gpto3mini      | 200,000         | 100,000          | Not specified          | Does not accept temperature, top_p, max_tokens; accepts max_completion_tokens          |
| gpto1          | 200,000         | 100,000          | Not specified          | Same as above                                                                         |
| gpto3          | -               | -                | -                      | Does not accept temperature, top_p, max_tokens; accepts max_completion_tokens          |
| gpto4mini      | -               | -                | -                      | Same as above                                                                         |
| gpt41          | 1,000,000       | 16,384           | -                      | Accepts temperature, top_p, max_completion_tokens                                     |
| gpt41mini      | 1,000,000       | 16,384           | -                      | Same as above                                                                         |
| gpt41nano      | 1,000,000       | 16,384           | -                      | Same as above                                                                         |
| gpt5           | 272,000         | 128,000          | Up to October 24, 2024 | Accepts temperature, top_p, max_completion_tokens; does not accept max_tokens          |
| gpt5mini       | 272,000         | 128,000          | Up to June 24, 2024    | Same as above                                                                         |
| gpt5nano       | 272,000         | 128,000          | Up to May 31, 2024     | Same as above                                                                         |

### Google

| Model ID       | Max Token Input | Max Token Output | Notes                                                                                   |
|----------------|-----------------|------------------|-----------------------------------------------------------------------------------------|
| gemini25pro    | 1,048,576       | 65,536           | Text-only model; maps Argo max_tokens to Gemini max_output_tokens                       |
| gemini25flash  | 1,048,576       | 64,536           | Text-only model; maps Argo max_tokens to Gemini max_output_tokens                       |

### Anthropic

| Model ID         | Max Token Input | Max Token Output | Notes                                                                                   |
|------------------|-----------------|------------------|-----------------------------------------------------------------------------------------|
| claudeopus41     | 200,000         | 32,000           | Text-only; requires user prompt content; defaults applied if max_tokens, temp, top_p missing |
| claudeopus4      | 200,000         | 32,000           | Same as above                                                                           |
| claudesonnet4    | 200,000         | 64,000           | Same as above                                                                           |
| claudesonnet37   | 200,000         | 128,000          | Same as above                                                                           |
| claudesonnet35v2 | 200,000         | 8,000            | Same as above                                                                           |

---

## Additional Fields

| Field              | Default | Type             | Optional | Description                                                                                     | Notes                          |
|--------------------|---------|------------------|----------|-------------------------------------------------------------------------------------------------|--------------------------------|
| stop               | null    | String or array  | Yes      | Up to four sequences where the API will stop generating further tokens. Returned text excludes stop sequence. | Not available for GPT o1-preview |
| temperature        | null    | number          | Yes      | Sampling temperature between 0 and 2. Higher means more risk-taking.                            | Not available for GPT o1-preview |
| top_p              | null    | number          | Yes      | Nucleus sampling alternative to temperature.                                                   | Not available for GPT o1-preview |
| max_tokens         | null    | integer         | Yes      | Maximum tokens to generate in completion. Prompt + max_tokens cannot exceed context length.    | Not available for GPT o1-preview |
| max_completion_tokens | null | integer         | Yes      | Only available for GPT o1-preview model                                                        |                                |

---

## Example & Code Template

Example Python scripts: `[argoapi_chat_test.py]` and `[argoapi_chat_messages_test.py]`

Example using the Postman API platform (using system + prompt fields):

Example using the Postman API platform (messages field):

---

## Endpoint: Embeddings

POST to (PROD environment)  
`https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/`  

or POST to (TEST environment)  
`https://apps-test.inside.anl.gov/argoapi/api/v1/resource/embed/`  

or POST to (DEV environment)  
`https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/embed/`

### Structure of the API Call Object

Required: Please include your personal Argonne domain account user name or a service account in the “user” field. This value is logged so we can track usage at the Division level. If you created a service account to represent calls from an application, then this name may be included in the “user” field instead.

```json
{
  "user": "<your ANL domain user, e.g., mdearing>",
  "model": "<required, input a valid name>",
  "prompt": [
    "string_one",
    "string_two",
    "string_three"
  ]
}
```

### Valid LLM Model Names for Embeddings

Three text embedding models are available for all users:

| Model ID | Description                 | Max Input Tokens | Output Dimension |
|----------|-----------------------------|------------------|------------------|
| ada002   | text-embedding-ada-002      | 8,191            | 1,536            |
| v3large  | text-embedding-3-large      | 8,191            | 3,072            |
| v3small  | text-embedding-3-small      | 8,191            | 1,536            |

Maximum number of elements in the prompt list: 16 – the return object will include a separate embedding as a 1D array/list for each string in the prompt list.

---

## End of Document

---

You can copy all the above text and save it as `Argo_API_Documentation.md` on your local machine.

If you'd like, I can also prepare a downloadable link for you if you prefer. Would you like me to do that?