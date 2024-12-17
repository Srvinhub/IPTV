import os
import requests

# 源文件链接
SOURCE_URL_IPV6_1 = os.getenv("SOURCE_URL_IPV6_1")
SOURCE_URL_IPV6_2 = os.getenv("SOURCE_URL_IPV6_2")

# 输出文件
OUTPUT_FILE = "live.m3u"

# 格式化函数生成频道信息
def format_channel_info(channel_name, logo_name, group_name, url):
    """
    格式化每个频道的信息，按照指定的 m3u 格式生成
    """
    return f'#EXTINF:-1 tvg-name="{channel_name}" tvg-logo="{logo_name}" group-title="{group_name}",{channel_name}\n{url}'

def fetch_m3u(url):
    """
    下载 M3U 文件
    """
    print(f"开始下载 M3U 文件: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("M3U 文件下载成功！")
            return response.text
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"下载错误: {e}")
        return None

def filter_and_group_channels(m3u_content, group_name_mapping):
    """
    筛选并重命名指定的group-title，返回格式化后的M3U内容
    """
    print(f"开始筛选并分组频道...")
    lines = m3u_content.splitlines()
    filtered_content = ["#EXTM3U"]  # 新的 M3U 文件头

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # 过滤出相关频道
            channel_name = line.split(",")[1].strip()
            url = lines[i + 1].strip()

            # 提取当前的 group-title
            group_title = None
            if 'group-title=' in line:
                group_title = line.split('group-title="')[1].split('"')[0]

            # 根据 group-title 映射进行重命名
            if group_title in group_name_mapping:
                new_group_title = group_name_mapping[group_title]
                formatted_channel = format_channel_info(channel_name, channel_name, new_group_title, url)
                filtered_content.append(formatted_channel)
            i += 2
        else:
            i += 1  # 跳过无关行

    print(f"频道筛选完成！")
    return "\n".join(filtered_content)

def merge_m3u(content1, content2):
    """
    合并两个 M3U 文件内容
    """
    print("开始合并 M3U 文件...")
    merged_content = []
    
    # 添加第一个文件内容
    merged_content.append(content1.strip())

    # 添加第二个文件内容
    merged_content.append(content2.strip())

    print("合并完成！")
    return "\n".join(merged_content)

def save_to_file(content, file_path):
    """
    保存内容到文件
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已保存到文件: {file_path}")

if __name__ == "__main__":
    # 下载两个源文件
    m3u_content_ipv6_1 = fetch_m3u(SOURCE_URL_IPV6_1)
    m3u_content_ipv6_2 = fetch_m3u(SOURCE_URL_IPV6_2)

    if m3u_content_ipv6_1 and m3u_content_ipv6_2:
        # 定义重命名映射：group-title
        group_name_mapping = {
            "港澳台频道": "港台频道",
            "港澳台AKTV": "港台电视",
            "电影轮播": "电影轮播",
            "电视剧轮播": "电视轮播",
            "埋堆堆": "埋堆堆剧",
            "春晚频道": "春晚频道",
            "国际频道": "国际频道"
        }

        # 从第二个源文件筛选并生成相关分组
        filtered_2 = filter_and_group_channels(m3u_content_ipv6_2, group_name_mapping)

        # 合并两个文件
        merged_m3u = merge_m3u(m3u_content_ipv6_1, filtered_2)

        # 保存到输出文件
        save_to_file(merged_m3u, OUTPUT_FILE)
    else:
        print("未能获取到所有源文件，程序结束。")
