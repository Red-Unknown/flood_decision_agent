data/ 存放数据层抽象与 mock 数据生成。

接口约定：
- MockDataGenerator.generate_all() -> dict[str, DataFrame]
- MockDataGenerator.validate_all(datasets) -> DataConsistencyReport

