"""Master-Sub Agent 测试脚本"""

import asyncio
from langchain_core.messages import HumanMessage

from src.agents.master_sub_agent import MasterSubAgent


async def test_master_sub_agent():
    """测试主控+子智能体系统"""
    print("=" * 60)
    print("主控+子智能体系统测试")
    print("=" * 60)

    # 创建智能体
    agent = MasterSubAgent()

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
    print("测试主控智能体调度子智能体")
    print("=" * 60)

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        print("-" * 60)

        try:
            # 创建测试上下文
            context = {
                "thread_id": "test_thread_master_sub_001",
                "user_id": "test_user_001",
            }

            # 调用智能体（只获取前几条消息以避免输出过长）
            message_count = 0
            async for message, metadata in agent.stream_messages(
                messages=[HumanMessage(content=test_input)],
                input_context=context,
            ):
                if hasattr(message, 'content'):
                    content_preview = str(message.content)[:200]
                    print(f"消息: {content_preview}...")
                    message_count += 1
                    if message_count >= 3:  # 只显示前3条消息
                        print("... (后续消息省略)")
                        break

        except Exception as e:
            print(f"测试出错: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_master_sub_agent())
