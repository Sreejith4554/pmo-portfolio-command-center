let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactMilestone.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"milestone_id", type text},
        {"project_id", type text},
        {"reporting_date", type date},
        {"milestone_name", type text},
        {"baseline_date", type date},
        {"forecast_date", type date},
        {"actual_date", type date},
        {"criticality", type text},
        {"days_variance", Int64.Type},
        {"overdue", Int64.Type},
        {"critical_overdue", Int64.Type},
        {"due_next_14_days", Int64.Type},
        {"status", type text}
    }, "en-US")
in
    Typed
