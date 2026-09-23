let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactDependency.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"dependency_id", type text},
        {"project_id", type text},
        {"upstream_project_id", type text},
        {"upstream_milestone_id", type text},
        {"downstream_task_id", type text},
        {"reporting_date", type date},
        {"owner_id", type text},
        {"lag_days", Int64.Type},
        {"criticality", type text},
        {"required_action", type text},
        {"available_date", type date},
        {"needed_date", type date},
        {"exposure_days", Int64.Type},
        {"upstream_project", type text},
        {"downstream_project", type text},
        {"status", type text},
        {"severe", Int64.Type}
    }, "en-US")
in
    Typed
