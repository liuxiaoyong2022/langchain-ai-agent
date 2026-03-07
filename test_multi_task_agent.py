"""多任务智能体测试脚本"""

import asyncio
from langchain_core.messages import HumanMessage

from src.agents.multi_task_agent import MultiTaskAgent


async def test_multi_task_agent():
    """测试多任务智能体"""
    print("=" * 60)
    print("多任务智能体测试")
    print("=" * 60)

    # 创建智能体
    agent = MultiTaskAgent()

    # 获取智能体信息
    info = await agent.get_info()
    print(f"\n智能体名称: {info['name']}")
    print(f"智能体描述: {info['description']}")
    print(f"支持的能力: {info['capabilities']}")

    # 获取图
    print("\n正在构建智能体图...")
    graph = await agent.get_graph()
    print("智能体图构建成功！")

    # 测试用例
    test_cases = [
        "帮我发个邮件",
        "帮我生成一张图片",
        "今天北京的天气怎么样",
        "把这段文字转成语音：你好世界",
        "制作一个数字人视频",
    ]

    print("\n" + "=" * 60)
    print("测试意图识别")
    print("=" * 60)

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        print("-" * 60)

        try:
            # 创建测试上下文
            context = {
                "thread_id": "test_thread_001",
                "user_id": "test_user_001",
            }

            # 调用智能体
            async for message, metadata in agent.stream_messages(
                messages=[HumanMessage(content=test_input)],
                input_context=context,
            ):
                if hasattr(message, 'content'):
                    print(f"响应: {message.content[:200]}...")  # 只显示前200字符
                print()

        except Exception as e:
            print(f"测试出错: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_multi_task_agent())
