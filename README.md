# Api Test Framework

The aim of this project is to test a series of API calls. Such calls can be independent from one another, but can also be dependent of previous ones.

#### Table Of Contents

- [Introduction](#introduction)
- [Quick start](#quick-start)
- [Main Concepts](#main-concepts)
- [Configuration](#configuration)
  - [Main Configuration Parameters](#main-configuration-parameters)
    - [headers](#headers)
  - [Test Suite Configuration Parameters](#test-suite-configuration-parameters)
    - [envOverride](#envoverride)
  - [Test Configuration Parameters](#test-configuration-parameters)
    - [responseCheckExceptions](#responsecheckexceptions)
    - [extract](#extract)
    - [inject](#inject)
- [Examples](#examples)
  - [Simple test](#simple-test)
  - [Extracting and Injecting values](#extracting-and-injecting-values)
- [Docker Image](#docker-image)

## Introduction

Imagine the following scenario: you have a set of APIs to book a hotel room.

A possible use case is as follows:

- User search for a room (`/search`).
  - This API returns a list of **`solutionID`s**.
- User selects a solution (`/reserve`).
  - This API requires a `solutionID`, retrieved using `/search`, and returns a **`reservationID`**.
- User finalize the booking (`/book`).
  - This API requires a `reservationID`, retrieved using `/reserve`.

Using this project we can execute the sequence of API calls, passing data from the result of a call to the next.

## Quick start

How to use:

1. Clone the project
2. Prepare configuration file (see the [Configuration](#configuration) section)
3. Prepare expected output files
4. Move to `src/` folder
5. Execute `python -m apitestframework <path/to/configuration/file.json>`

## Main Concepts

Each run of the program is a **`Test Run`**.

A `Test Run` is composed of a list of **`Test Suites`**.

Each `Test Suite` is composed of a sequence of **`Api Tests`**.

A `Test Run` is defined by a configuration file. When executing the program passing multiple configuration files we can run multiple Test Runs.

## Configuration

Most of the parameters are optionals (where it makes sense), and if not found a default value is applied.

See the following configuration file example. This will execute the sequence of calls:

1. `GET /status` to check that the enpoint is available
2. `POST /search` to retrieve a list of solutions
3. `POST /reservation` to "block" solution
4. `POST /book` to finalize the process
5. `DELETE /book` to cancel the booking

```json
{
    "logLevel": 20,
    "headers": {
        "Content-Type": {
            "value": "application/json"
        },
        "Accept": {
            "value": "application/json"
        }
    },
    "suites": [
        {
            "name": "HOTEL_BOOKING",
            "headers": {
                "Authorization": {
                    "value": "Basic {}",
                    "envName": "API_TOKEN"
                }
            },
            "envOverride": [
                {
                    "name": "baseUrl",
                    "envName": "API_BASE_URL"
                }
            ],
            "tests": [
                {
                    "name": "Status",
                    "url": "/status",
                    "expected": "output/status-expected.json"
                },
                {
                    "name": "Search",
                    "url": "/search",
                    "method": "POST",
                    "payload": {
                        "currency": "EUR",
                        "language": "en",
                        "hotelCode": "09400",
                        "arrivalDate": "2019-08-30",
                        "departureDate": "2019-09-02",
                        "guests": {
                            "adult": 1,
                            "child": 0,
                            "infant": 0
                        }
                    },
                    "expected": "output/search-expected.json",
                    "extract": [
                        {
                            "name": "solutionId",
                            "key": "solutions.0.solutionId"
                        }
                    ]
                },
                {
                    "name": "Reservation",
                    "url": "/reservation",
                    "method": "POST",
                    "payload": {
                        "solutionId": null
                    },
                    "expected": "output/reservation-expected.json",
                    "responseCheckExceptions": [
                        {
                            "key": "reservationId",
                            "type": "exist"
                        }
                    ],
                    "extract": [
                        {
                            "name": "reservationId",
                            "key": "reservationId"
                        }
                    ],
                    "inject": [
                        {
                            "name": "solutionId",
                            "type": "body",
                            "key": "solutionId"
                        }
                    ]
                },
                {
                    "name": "Booking",
                    "url": "/booking",
                    "method": "POST",
                    "payload": {
                        "reservationId": null
                    },
                    "expected": "output/booking-expected.json",
                    "responseCheckExceptions": [
                        {
                            "key": "bookingId",
                            "type": "exist"
                        }
                    ],
                    "extract": [
                        {
                            "name": "bookingId",
                            "key": "bookingId"
                        }
                    ],
                    "inject": [
                        {
                            "name": "reservationId",
                            "type": "body",
                            "key": "reservationId"
                        }
                    ]
                },
                {
                    "name": "Delete Booking",
                    "url": "/booking",
                    "method": "DELETE",
                    "params": {
                        "force": true
                    },
                    "expected": "output/deletebooking-expected.json",
                    "inject": [
                        {
                            "name": "bookingId",
                            "type": "path"
                        }
                    ]
                }
            ]
        }
    ]
}
```

### Main Configuration Parameters

At root level, the configuration file contains only two parameters:

| Parameter name | Purpose                                                   | Possible values                                            | Default value |
| -------------- | --------------------------------------------------------- | ---------------------------------------------------------- | ------------- |
| `logLevel`     | Determine the importance level of printed output messages | `10`: DEBUG<br>`20`: INFO<br>`30`: WARN<br>`40`: ERROR<br> | `10`          |
| `headers`      | Set of Headers to apply to each test call of every suite  | `"<header-key>": { <header_definition> }`                  | **N/A**       |
| `suites`       | List of Test Suites                                       | Array of Tests Suites                                      | `[]`          |

#### headers

Elements in this configuration parameter must be in this format:

```json
"<header-key>": {
    "value": "<header-value>",
    "placeholder": "{}",
    "envName": "<env-var-name>",
    "hide": false
}
```

Where

- `<header-key>` is the name of the header. Standard headers names are, for example, "Content-Type", or "Accept". (See [List of HTTP header fields](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#Request_fields) for more examples)
- `<header-value>` is the value to set the header to. Defaults to empty string
- `placeholder` is a string contained in the header value that will be replaced with the content of an environment variable. Its default is "{}"
- `<env-var-name>` is the name of the environment variable to use. This is case-sensitive.
- `hide` determines whether this header is to be included in the call. Useful when a particular header is needed in every test of the suite expect a few ones. Default is `false`

The `headers` field can be found at every level of the configuration (Test Run, Test Suite and Api Test). Inner levels declaration of a header defined at outer ones will replace the original definition for those levels.

### Test Suite Configuration Parameters

At single Test Suite level, the configuration file can contain the following parameters:

| Parameter name  | Purpose                                                          | Possible values                                                | Default value                              |
| --------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------ |
| `name`          | Name of the Test Suite                                           | A string                                                       | `Unnamed Test Suite - <current timestamp>` |
| `exitOnFailure` | Whether to exit at the first test failure or execute all of them | `true`/`false`                                                 | `true`                                     |
| `baseUrl`       | The base URl for all the calls in the Test Suite                 | A valid URL composed of protocol, address and port (if needed) | **N/A** (will exit if missing)             |
| `headers`       | Set of Headers to apply to each test call                        | `"<header-key>": { <header_definition> }`                      | **N/A**                                    |
| `verifySsl`     | Whether to validate the SSL certificate of the endpoint          | `true`/`false`                                                 | `true`                                     |
| `envOverride`   | List of parameters to override with environment variables        | `[{"name": "<parameter-name>", "envName": "<env-var-name>"}]`  | `[]`                                       |
| `tests`         | List of Tests                                                    | Array of Tests                                                 | `[]`                                       |

#### envOverride

Elements in this configuration parameter must be in this format:

```json
{
    "name": "<parameter-name>",
    "envName": "<env-var-name>"
}
```

Where

- `<parameter-name>` is one of the Test Suite Configuration Parameters. The value of this field must be exactly the name of the parameter it overrides, obviously.
- `<env-var-name>` is the name of the environment variable to use. This is case-sensitive.

These environment values are applied after the configuration values, hence overriding them.

This means that if you declare `baseUrl` in the configuration, but also in the `envOverride`, the configuration value will be replaced with the environment one. Make sure that the environment variables are set, or you'll end up with empty values.

### Test Configuration Parameters

At single Test level, the configuration file can contain the following parameters:

| Parameter name            | Purpose                                                                   | Possible values                                                                          | Default value                                    |
| ------------------------- | ------------------------------------------------------------------------- | -----------------------------------------------------------------------------------------| ------------------------------------------------ |
| `name`                    | Name of the Test                                                          | A string                                                                                 | `Unnamed Test - <current timestamp>`             |
| `headers`                 | Set of Headers to apply to the test call                                  | `"<header-key>": { <header_definition> }`                                                | **N/A**                                          |
| `enabled`                 | Whether to run this test or not                                           | `true`/`false`                                                                           | `true`                                           |
| `path`                    | Path to add to `baseUrl` for the call                                     | E.g. `/v1/search`                                                                        | Empty string                                     |
| `method`                  | HTTP method for the call                                                  | `GET`, `POST`, `DELETE`, etc.                                                            | `GET`                                            |
| `payload`                 | JSON body for the call                                                    | A valid JSON                                                                             | **N/A**                                          |
| `params`                  | JSON object representing the URL parameters to add to the call            | A valid JSON                                                                             | **N/A**                                          |
| `expected`                | Path to file containing the expected result body. Will be loaded as JSON  | A path (absolute or relative (to current folder)). E.g. `../output/search-expected.json` | **N/A** (will exit if missing parameter or file) |
| `expected_code`           | Expected return code of the call                                          | `200`, `400`, etc.                                                                       | `200`                                            |
| `responseCheckExceptions` | Fields to ignore when checking result                                     | `[{"key": "<field-key>", "type": "<exception-type>"}]`                                   | `[]`                                             |
| `extract`                 | Fields to extract from the result to use in subsequent calls              | `[{"name": "<field-name>", "key": "<field-key>"}]`                                       | `[]`                                             |
| `inject`                  | Fields that need to be injected into the test for the call to be complete | `[{"name": "<field-name>", "type": "<field-type>", "key": "<field-key>"}]`               | `[]`                                             |

#### responseCheckExceptions

Each exception uses this format:

```json
{
    "key": "<field-key>",
    "type": "<exception-type>"
}
```

Where:

- `<field-key>` is the "path" inside the object expressed in **dot-notation**. E.g. if you have a response object like this:

    ```json
    {
        "currency": "EUR",
        "solutions": [
            {
                "solutionId": "32iuhr3782yr4e7283j",
                "departureDateTime": "2019-03-02T12:20:00+02:00",
                "arrivalDateTime": "2019-08-30T12:40:00+02:00",
                "totalPrice": 180
            },
            {
                "solutionId": "28endwqjf83oijewmdo",
                "departureDateTime": "2019-03-03T13:15:00+02:00",
                "arrivalDateTime": "2019-08-31T16:00:00+02:00",
                "totalPrice": 210
            }
        ]
    ```

    Fields key are like this:

    - `currency`
    - `solutions.0.solutionId`

    Currently there is no way to specify an exception for whole arrays or objects, nor to use wildcards (e.g. `solutions` or `solutions.*.solutionId` won't work)

    **Note**: the fields to check stem from the `expected` file. This means that if the response has fields not included in the expected file, they're ignored by default.

- `<exception-type>` specify what kind of exception we want to apply. Currently we support:

  - `ignore`: we completely skip the check on this value. If the result doesn't even contain this field, it won't result in an error
  - `exist`: we check whether the field exist, but we do not compare the result value with the expected one

#### extract

Each "extract" field is in this format:

```json
{
    "name": "<field-name>",
    "key": "<field-key>"
}
```

Where:

- `<field-name>` is the name to match for subsequent "inject"
- `<field-key>` is as explained in the [responseCheckExceptions](#responsecheckexceptions) section

Extracted values are "Test Suite-global". This means that a field extracted in a test, can be used in any other subsequent ones.

Please note that extract more than one field with the same `<field-name>` will overwrite previous values of it.

If a value to extract is not found, it will be set to `None`.

#### inject

Each "inject" field  is in this format:

```json
{
    "name": "<field-name>",
    "key": "<field-key>",
    "type": "<field-type>"
}
```

Where:

- `<field-name>` is the name to match with previous "extract"
- `<field-key>` is as explained in the [responseCheckExceptions](#responsecheckexceptions) section
- `<field-type>` determines how a value will be used by the test when it runs. Currently we support:

  - `body`: a field identified by the specified `<field-key>` in the request body will be set to the value of the extracted field
  - `query`: a query parameter identified by the specified `<field-key>` in the URL will be set to the value of the extracted field
  - `path`: the value of the extracted field will be appended to the test URL, prepended by a `/`
  - `header`: a header identified by the specified `<field-key>` will be set to the value of the extracted field. If the header already exists, its value will be updated, otherwise a new header will be created

## Examples

We will now further describe the various behaviors, using the above configuration. Suppose that `baseUrl=http://192.168.0.1:8080`

### Simple test

Given this simple test configuration:

```json
{
    "name": "Status",
    "url": "/status",
    "expected": "output/status-expected.json"
}
```

And this `output/status-expected.json` file:

```json
{
    "version": "0.0.1",
    "status": "OK"
}
```

This will perform a `GET http://192.168.0.1:8080/status` and check that the result body has both the `version` and `status` fields with values `0.3.1` and `OK`, respectively.

### Extracting and Injecting values

Given this configuration:

```json
{
    "name": "Search",
    "url": "/search",
    "method": "POST",
    "payload": {
        "hotelCode": "09400",
        "arrivalDate": "2019-08-30",
        "departureDate": "2019-09-02",
        "guests": {
            "adult": 1,
            "child": 0,
            "infant": 0
        }
    },
    "expected": "output/search-expected.json",
    "extract": [
        {
            "name": "solutionId",
            "key": "solutions.0.solutionId"
        }
    ]
},
{
    "name": "Reservation",
    "url": "/reservation",
    "method": "POST",
    "payload": {
        "solutionId": null
    },
    "expected": "output/reservation-expected.json",
    "responseCheckExceptions": [
        {
            "key": "reservationId",
            "type": "exist"
        }
    ],
    "extract": [],
    "inject": [
        {
            "name": "solutionId",
            "type": "body",
            "key": "solutionId"
        }
    ]
}
```

And the following `output/search-expected.json`:

```json
{
    "solutions": [{
        "solutionId": "32iuhr3782yr4e7283j",
        ...
```

and `output/reservation-expected.json`:

```json
{
    "reservationId": "2687hgr87u1"
}
```

This will perform a `POST http://192.168.0.1:8080/search` with body `<payload>` (see above) and from its response will extract the `solutionId` field, with the rules described above.

Then will inject into the next text the `solutionId` just extracted and perform a `POST http://192.168.0.1:8080/reservation`.

When checking the result of this second call will just make sure that the response has the `reservationId` field, but without looking at its value.

---

## Docker Image

Start like this:

```bash
$> docker run -it -v "/path/to/config/folder":/config -e CONFIG_FILE=config.json --env-file ./.env gitlab.jmatica.com:4567/jmatica/api-test-framework:latest
```

Where:

- `/path/to/config/folder` is a folder containing the `config.json` file
- `.env` is a file containing environment variable to inject into the container (see [envOverride](#envoverride))
