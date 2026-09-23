let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactIssue.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"issue_id", type text},
        {"project_id", type text},
        {"reporting_date", type date},
        {"title", type text},
        {"owner_id", type text},
        {"severity", type text},
        {"status", type text},
        {"opened_date", type date},
        {"due_date", type date},
        {"resolution_date", type date},
        {"required_action", type text},
        {"age_days", Int64.Type},
        {"overdue", Int64.Type},
        {"critical", Int64.Type},
        {"escalation_status", type text},
        {"owner", type text}
    }, "en-US")
in
    Typed
