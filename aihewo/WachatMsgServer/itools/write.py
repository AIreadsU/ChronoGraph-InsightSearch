
import pandas as pd
from neo4j import GraphDatabase
#from llama_index.graph_stores.neo4j import Neo4jGraphStore
import time
import urllib.request
from ..models import Contact, WeChatMessage, PhoneData, ChartData



#测试neo4j 地址
# NEO4J_URI="neo4j://101.126.156.86:7687"
# NEO4J_USERNAME="neo4j"
# NEO4J_PASSWORD="0LeFyTf4n4odfmMwQBuy"
# NEO4J_DATABASE="neo4j"

'''
# 数据库连接相关参数配置
NEO4J_URI="neo4j://127.0.0.1:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="Jssq1234"
NEO4J_DATABASE="neo4j"
'''

def init(NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD,NEO4J_DATABASE):
    NEO4J_URI = NEO4J_URI
    NEO4J_USERNAME = NEO4J_USERNAME
    NEO4J_PASSWORD = NEO4J_PASSWORD
    NEO4J_DATABASE = NEO4J_DATABASE

    # 实例化一个图数据库实例
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    return driver,NEO4J_DATABASE

# 使用批处理方式将数据帧导入Neo4j
# 参数：statement 是要执行的 Cypher 查询，df 是要导入的数据帧，batch_size 是每批要导入的行数
def batched_import(driver,NEO4J_DATABASE,statement, df, batch_size=1000):
    # 计算数据帧df中的总行数，并将其存储在total变量中
    total = len(df)
    # 记录当前时间，以便后续计算导入操作所花费的总时间
    start_s = time.time()
    # 每次循环处理一批数据，步数为batch_size
    for start in range(0,total, batch_size):
        # 使用Pandas的iloc方法提取当前批次的数据子集
        # start是当前批次的起始行号
        # min(start + batch_size, total)是当前批次的结束行号，确保不会超过总行数
        batch = df.iloc[start: min(start+batch_size,total)]
        # "UNWIND $rows AS value "是Cypher中的一个操作，它将 $row中的每个元素逐个解包，并作为value传递给Cypher语句statement
        result = driver.execute_query("UNWIND $rows AS value " + statement,
                                      # 将当前批次的 DataFrame 转换为字典的列表
                                      # 每一行数据变成一个字典，columns 作为键
                                      rows=batch.to_dict('records'),
                                      database_=NEO4J_DATABASE)
        # 打印执行结果的摘要统计信息，包括创建的节点、关系等计数
        print(result.summary.counters)
    # 计算并打印导入总行数和耗时
    print(f'{total} rows in { time.time() - start_s} s.')
    # 返回导入的总行数
    return total

def http_get(url):
    response = urllib.request.urlopen(url)
    content = response.read()
    return content.decode('utf-8')


# 按顺序依次执行如下步骤
def read_newdate(phone_number,NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD,NEO4J_DATABASE):
    driver, NEO4J_DATABASE = init (NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD,NEO4J_DATABASE)
    phone_number = phone_number
    contacts = Contact.objects.filter(phone_number=phone_number, is_valid=True).select_related('phone_data')

    doc_df = []
    for contact in contacts:
        messages = contact.wechatmessage_set.all()
        if messages.exists():
            user_date_info = {
                'user_name': contact.user_name,
                'alias': contact.alias,
                'type': contact.type,
                'remark': contact.remark,
                'nick_name': contact.nick_name,
                'small_head_img_url': contact.small_head_img_url,
                'detail': contact.detail,
                'label_name': contact.label_name,
                'phone_number': contact.phone_number,
            }
            doc_df.append(user_date_info)

    doc_df=doc_df.fillna('')
    statement = """
    MERGE (u1:user {phone_number:''})
    MERGE (u2:user {user_name:value.user_name,alias:value.alias,type:value.type,remark:value.remark,nick_name:value.nick_name,small_head_img_url:value.small_head_img_url,detail:value.detail,label_name:value.label_name})
    MERGE (u1)-[:l]-(u2)
    """
    total = batched_import(driver,NEO4J_DATABASE,statement, doc_df)
    print("返回的结果：",total)

    '''
    
    MERGE (u1:user {phone_number:"57074592332@chatroom",nick_name:'RAGFlow 社区 10 群',small_head_img_url='https://wx.qlogo.cn/mmcrhead/GibvHudxmlJZEPqn16w6baicsg0XxlVSPmfhiavcJYXnib0AQPZ5dD2bic1SGXqVuQabXw24oibk5h6Rw/0'})
    MERGE (u2:user {user_name:"57074592332@chatroom"})
    MERGE (u1)-[:l]-(u2)
    '''

NEO4J_URI = "neo4j://101.126.156.86:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "0LeFyTf4n4odfmMwQBuy"
NEO4J_DATABASE = "neo4j"
read_newdate('15000537641',NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD,NEO4J_DATABASE)