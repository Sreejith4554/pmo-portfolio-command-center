let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactCost.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"cost_id", type text},
        {"project_id", type text},
        {"transaction_date", type date},
        {"category", type text},
        {"amount", Int64.Type}
    }, "en-US")
in
    Typed
