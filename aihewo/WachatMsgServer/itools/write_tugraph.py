# from neo4j import GraphDatabase
#
# import time
# import json
# from neo4j import GraphDatabase
#
# import pandas as pd
#
#
# class Tugraph:
#     def __init__(self, uri, user, password):
#         # URI = "bolt://127.0.0.1:7687"
#         # AUTH = ("admin", "73@TuGraph")
#         URI = uri
#         AUTH = (user, password)
#         client = GraphDatabase.driver(URI, auth=AUTH)
#         self.session = client.session(database="default")
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))
#
#     def close(self):
#         self.driver.close()
#
#     def create_node(self, label, properties):
#         with self.driver.session() as session:
#             # 构建Cypher查询语句，用于创建一个具有指定标签和属性的节点
#             query = f"CREATE (n:{label} $properties)"
#             # 执行Cypher查询语句，将节点创建在数据库中
#             session.run(query, properties=properties)
#
#     def batched_import(self,statement, df):
#         # 计算数据帧df中的总行数，并将其存储在total变量中
#         total = len(df)
#         # 记录当前时间，以便后续计算导入操作所花费的总时间
#         start_s = time.time()
#         # 每次循环处理一批数据，步数为batch_size
#         for start in range(0,total,1):
#             # 使用Pandas的iloc方法提取当前批次的数据子集
#             try:
#                 value=df.iloc[start].to_dict()
#                 print(statement.format(**value))
#                 # "UNWIND $rows AS value "是Cypher中的一个操作，它将 $row中的每个元素逐个解包，并作为value传递给Cypher语句statement
#                 self.session.run(statement.format(**value))
#             except Exception as e:
#                 print(e)
#             # 打印执行结果的摘要统计信息，包括创建的节点、关系等计数
#         # 计算并打印导入总行数和耗时
#         print(f'{total} rows in { time.time() - start_s} s.')
#         # 返回导入的总行数
#         return total
#
#
#     def inster_sql(self,data,phoneNumber,userName):
#         # doc_df = pd.read_csv('data/get_contacts_with_messages.csv')
#         #doc_df.rename(columns={'UserName': 'id'}, inplace=True)
#         doc_df = data
#         print(doc_df.head(30))
#
#         doc_df=doc_df.fillna('')
#         statement = """
#         MERGE (u1:user {phone_number:''})
#         MERGE
#         MERGE (u1)-[:l]-(u2)
#         """
#
#
#         query="""
#         CREATE (qy1:qy {{nsrsbh:"{Nsrsbh}",nsrmc:"{Nsrmc}",swjgdm_ds:"{Ds}"}})
#         CREATE (zrr1:zrr {{xm:"{xm}",sfzjhm:"{ZJHM}"}})
#         CREATE (qy1)-[:rygx{{sf_bz:"{SF_BZ}"}}]->(zrr1)
#         """
#         # query1="""
#         # CREATE (u1:user {{phone_number:'15000537641',user_name:'15000537641'}})
#         # """
#         query1 = """
#         CREATE (u1:user {phone_number: $phoneNumber, user_name: $userName})
#         """
#         query2="""
#         CREATE (u2:user {{user_name:"{user_name}",alias:"{alias}",type:"{type}",remark:"{remark}",nick_name:"{nick_name}",small_head_img_url:"{small_head_img_url}",detail:"{detail}",label_name:"{label_name}"}})
#         """
#         # query3="""
#         # match (u1:user {{phone_number:'15000537641'}}), (u2:user {{user_name:"{user_name}"}}) CREATE (u1)-[:relation]->(u2)
#         # """
#         query3 = """
#         MATCH (u1:user {phone_number: $phoneNumber}), (u2:user {user_name: $userName})
#         CREATE (u1)-[:relation]->(u2)
#         """
#         self.batched_import(query1,phoneNumber=phoneNumber, userName=userName)
#         self.batched_import(query2,doc_df)
#         self.batched_import(query3,phoneNumber=phoneNumber, userName=userName)
#
#         self.close()

from neo4j import GraphDatabase
import pandas as pd
import time


class Tugraph:
    def __init__(self, uri, user, password,databasename):
        self.admin = user
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = self.driver.session(database=databasename)

    def close(self):
        self.session.close()
        self.driver.close()

    # def execute_query(self, query, **params):
    #     self.session.run(query, **params)

    # def batch_process_df(self, query_template, df, batch_size=1000):
    #     total = len(df)
    #     start_time = time.time()
    #     tx = self.session.begin_transaction()
    #     try:
    #         for i in range(0, total, batch_size):
    #             batch_df = df.iloc[i:i + batch_size]
    #             for _, row in batch_df.iterrows():
    #                 params = row.to_dict()
    #                 tx.run(query_template, **params)
    #             if (i + batch_size) % (batch_size * 10) == 0:  # 每处理10个batch提交一次，减少内存占用
    #                 tx.commit()
    #                 tx = self.session.begin_transaction()
    #         tx.commit()  # 提交剩余的事务
    #     except Exception as e:
    #         tx.rollback()  # 发生错误时回滚
    #         print(f"Error processing batch: {e}")
    #     finally:
    #         if tx.is_open():
    #             tx.rollback()  # 确保事务被关闭
    #     print(f'{total} rows processed in {time.time() - start_time} s.')

    def batched_import(self,statement, df):
        # 计算数据帧df中的总行数，并将其存储在total变量中
        total = len(df)
        # 记录当前时间，以便后续计算导入操作所花费的总时间
        start_s = time.time()
        # 每次循环处理一批数据，步数为batch_size
        for start in range(0,total,1):
            # 使用Pandas的iloc方法提取当前批次的数据子集
            try:
                value=df.iloc[start].to_dict()
                print(statement.format(**value))
                # "UNWIND $rows AS value "是Cypher中的一个操作，它将 $row中的每个元素逐个解包，并作为value传递给Cypher语句statement
                self.session.run(statement.format(**value))
            except Exception as e:
                print(e)
            # 打印执行结果的摘要统计信息，包括创建的节点、关系等计数
        # 计算并打印导入总行数和耗时
        print(f'{total} rows in { time.time() - start_s} s.')
        # 返回导入的总行数
        return total

    def insert_data(self, data, userName, phoneNumber):
        doc_df = data.fillna('')  # 注意：这可能会影响数据的完整性

        query1 = """
        CREATE (u1:user {{phone_number:'%s',user_name:'%s'}})
        """%(userName, phoneNumber)
        query2 = """
                CREATE (u2:user {{user_name:"{user_name}",alias:"{alias}",type:"{type}",remark:"{remark}",nick_name:"{nick_name}",small_head_img_url:"{small_head_img_url}",detail:"{detail}",label_name:"{label_name}"}})
                """
        query3 = """
                match (u1:user {{phone_number:'%s'}}), (u2:user {{user_name:"{user_name}"}}) CREATE (u1)-[:relation]->(u2)
                """%(phoneNumber)

        self.batched_import(query1, doc_df)
        self.batched_import(query2, doc_df)
        self.batched_import(query3,  doc_df)

    # 使用示例
# 注意：在实际使用中，您需要提供正确的URI、用户名、密码以及DataFrame数据
# tugraph = Tugraph(uri="bolt://localhost:7687", user="neo4j", password="password")
# tugraph.insert_data(pd.DataFrame(...), "1234567890", "username")
# tugraph.close()