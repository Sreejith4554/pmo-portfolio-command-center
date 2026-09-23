let
    Source = Csv.Document(File.Contents(BaseFolder & "/DimPeriod.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"reporting_date", type date},
        {"period_index", Int64.Type},
        {"period_label", type text}
    }, "en-US")
in
    Typed
