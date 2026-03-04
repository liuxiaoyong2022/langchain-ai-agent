
### 用pytest进行测试
可尝试以下步骤：
1. 安装 `pytest` 以及 `pytest_asyncio`
   ```pytest
   pip install pytest
   pip install pytest_asyncio    
   ```
2. 创建 `.evn.test` 并初始化user参数：
   ```evn.test
    TEST_BASE_URL=http://localhost:5050

   # 测试用户凭据
     TEST_USERNAME=admin1
     TEST_PASSWORD=abcd1234.  
   # 测试服务器地址
     TEST_BASE_URL=http://localhost:5050
   ```
3. 运行指定的测试案例 ：
   ```pytest
   pytest test/test_mysql_connection.py
   ```
   输出如下
   ```
   =========================================================================================== test session starts ===========================================================================================
    platform darwin -- Python 3.12.4, pytest-9.0.2, pluggy-1.6.0 -- /opt/miniconda3/envs/langchain-dev/bin/python3.12
    cachedir: .pytest_cache
    rootdir: /Volumes/Lxy-Data-Vol/export/dev/project/python/gitee/langchain-ai-agent
    configfile: pyproject.toml
    plugins: anyio-4.12.0, Faker-40.4.0, asyncio-1.3.0, langsmith-0.4.56
    asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
    collected 2 items                                                                                                                                                                                         

    test/test_mysql_connection.py::test_mysql_connection         PASSED                               [ 50%]
    test/test_mysql_connection.py::test_tools                    PASSED                               [100%]
   ```


