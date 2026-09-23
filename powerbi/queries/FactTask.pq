let
    Source = Csv.Document(File.Contents(BaseFolder & "/FactTask.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"task_id", type text},
        {"project_id", type text},
        {"reporting_date", type date},
        {"task_name", type text},
        {"planned_start", type date},
        {"due_date", type date},
        {"actual_finish", type date},
        {"owner_id", type text}
    }, "en-US")
in
    Typed
