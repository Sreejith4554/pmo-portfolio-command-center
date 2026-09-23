let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactResource.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"resource_id", type text},
        {"resource_name", type text},
        {"role", type text},
        {"weekly_capacity_hours", Int64.Type},
        {"reporting_date", type date},
        {"allocated_hours", Int64.Type},
        {"capacity_hours", type number},
        {"utilisation_pct", type number},
        {"overload_hours", type number}
    }, "en-US")
in
    Typed
