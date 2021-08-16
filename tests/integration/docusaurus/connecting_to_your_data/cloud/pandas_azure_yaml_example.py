from ruamel import yaml

import great_expectations as ge
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest

context = ge.get_context()

datasource_yaml = f"""
name: my_azure_datasource
class_name: Datasource
execution_engine:
    class_name: PandasExecutionEngine
    azure_options:
        account_url: <YOUR_ACCOUNT_URL> # or `conn_str`
        credential: <YOUR_CREDENTIAL>   # if using a protected container
data_connectors:
    default_runtime_data_connector_name:
        class_name: RuntimeDataConnector
        batch_identifiers:
            - default_identifier_name
    default_configured_data_connector_name:
        class_name: ConfiguredAssetAzureDataConnector
        azure_options:
            account_url: <YOUR_ACCOUNT_URL> # or `conn_str`
            credential: <YOUR_CREDENTIAL>   # if using a protected container
        container: <YOUR_AZURE_CONTAINER_HERE>
        name_starts_with: <CONTAINER_PATH_TO_DATA>
        default_regex:
            pattern: 2019/yellow_trip_data_sample_(\\d{{4}})-(\\d{{2}})\\.csv
            group_names:
                - year
                - month
        assets:
            taxi:
"""

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your path directly in the yaml above.
datasource_yaml = datasource_yaml.replace(
    "<YOUR_AZURE_CONTAINER_HERE>", "superconductive-public"
)
datasource_yaml = datasource_yaml.replace("<CONTAINER_PATH_TO_DATA>", "2019/")
datasource_yaml = datasource_yaml.replace(
    "<YOUR_ACCOUNT_URL>", "superconductivetests.blob.core.windows.net"
)
datasource_yaml = datasource_yaml.replace(  # We are using a public container
    "credential: <YOUR_CREDENTIAL>", ""
)

context.test_yaml_config(datasource_yaml)

context.add_datasource(**yaml.load(datasource_yaml))

# Here is a RuntimeBatchRequest using a path to a single CSV file
batch_request = RuntimeBatchRequest(
    datasource_name="my_azure_datasource",
    data_connector_name="default_runtime_data_connector_name",
    data_asset_name="<YOUR_MEANGINGFUL_NAME>",  # this can be anything that identifies this data_asset for you
    runtime_parameters={
        "path": "<PATH_TO_YOUR_DATA_HERE>"
    },  # add your Azure path here.
    batch_identifiers={"default_identifier_name": "something_something"},
)

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your path directly in the BatchRequest above.
batch_request.runtime_parameters[
    "path"
] = "superconductivetests.blob.core.windows.net/superconductive-public/2019/yellow_trip_data_sample_2019-01.csv"

context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)

validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)

print(validator.head())

# NOTE: The following code is only for testing and can be ignored by users.
assert isinstance(validator, ge.validator.validator.Validator)

# Here is a BatchRequest naming a data_asset
batch_request = BatchRequest(
    datasource_name="my_azure_datasource",
    data_connector_name="default_configured_data_connector_name",
    data_asset_name="<YOUR_DATA_ASSET_NAME>",
)

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your data asset name directly in the BatchRequest above.
batch_request.data_asset_name = "taxi"

context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())


# NOTE: The following code is only for testing and can be ignored by users.
assert isinstance(validator, ge.validator.validator.Validator)
assert [ds["name"] for ds in context.list_datasources()] == ["my_azure_datasource"]
assert set(
    context.get_available_data_asset_names()["my_azure_datasource"][
        "default_configured_data_connector_name"
    ]
) == {
    "2019/yellow_trip_data_sample_2019-01.csv",
    "2019/yellow_trip_data_sample_2019-02.csv",
    "2019/yellow_trip_data_sample_2019-03.csv",
}
