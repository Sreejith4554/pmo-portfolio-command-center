let
    Source = Csv.Document(File.Contents(BaseFolder & "/DimUpstreamProject.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"upstream_project_id", type text},
        {"upstream_project_name", type text}
    }, "en-US")
in
    Typed
