let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactAction.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"action_id", type text},
        {"project_id", type text},
        {"reporting_date", type date},
        {"title", type text},
        {"owner_id", type text},
        {"due_date", type date},
        {"status", type text},
        {"priority", type text},
        {"overdue", Int64.Type},
        {"owner", type text}
    }, "en-US")
in
    Typed
