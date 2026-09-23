let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactAllocation.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"allocation_id", type text},
        {"project_id", type text},
        {"resource_id", type text},
        {"reporting_date", type date},
        {"allocated_hours", Int64.Type}
    }, "en-US")
in
    Typed
