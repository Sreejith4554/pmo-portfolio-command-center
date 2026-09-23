let
    Source = Csv.Document(File.Contents(BaseFolder & "/DimProject.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"project_id", type text},
        {"project_name", type text},
        {"department_id", type text},
        {"manager_id", type text},
        {"sponsor_id", type text},
        {"priority", type text},
        {"planned_start", type date},
        {"planned_finish", type date},
        {"story", type text},
        {"department", type text},
        {"manager", type text},
        {"sponsor", type text}
    }, "en-US")
in
    Typed
