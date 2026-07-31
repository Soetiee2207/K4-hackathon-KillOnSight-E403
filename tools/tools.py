import json
import os
import urllib.request
import urllib.error

# Load API_KEY từ file .env (ở thư mục gốc)
env_path = '../.env' if os.path.exists('../.env') else '.env'
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------
# 1. PHẦN THỰC THI TOOL (MOCK DATA CHO DEMO)
# ---------------------------------------------------------
def get_current_slide_content():
    """Hàm Python thật để lấy nội dung màn hình."""
    print(">> [Hệ thống] Đang chạy hàm get_current_slide_content()...")
    return "Nội dung trang hiện tại: 3 Hướng làm sản phẩm AI bao gồm Trợ lý Học viên, Trợ lý Giảng viên, và Trợ lý Vận hành. Lưu ý: Không dùng data thật."

def search_course_materials(query):
    """Hàm Python thật để tìm kiếm tài liệu."""
    print(f">> [Hệ thống] Đang chạy hàm search_course_materials(query='{query}')...")
    return f"Kết quả tìm kiếm cho '{query}': Nó là một khái niệm được dạy ở Buổi 1, dùng để đo lường hiệu suất mô hình."

def analyze_slide_image(page_number):
    print(f">> [Hệ thống] Đang phân tích ảnh ở trang {page_number}...")
    return f"Phân tích ảnh trang {page_number}: Sơ đồ này biểu diễn quy trình xử lý dữ liệu đầu vào."

def save_concept_to_flashcard(concept_name, explanation):
    print(f">> [Hệ thống] Đã lưu '{concept_name}' vào CSDL Flashcard cá nhân!")
    return "Lưu flashcard thành công."

# Mapping tên hàm (string từ AI) sang hàm Python thật
AVAILABLE_TOOLS = {
    "get_current_slide_content": get_current_slide_content,
    "search_course_materials": search_course_materials,
    "analyze_slide_image": analyze_slide_image,
    "save_concept_to_flashcard": save_concept_to_flashcard
}

# ---------------------------------------------------------
# 2. LOAD CẤU TRÚC JSON ĐỂ DẠY AI BIẾT CÁC TOOLS NÀY
# ---------------------------------------------------------
def load_tools_schema():
    schema_path = 'ai_tools_schema.json'
    if not os.path.exists(schema_path):
        print("Lỗi: Không tìm thấy file ai_tools_schema.json")
        return []
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ---------------------------------------------------------
# 3. HÀM TƯƠNG TÁC VỚI GROQ VÀ TỰ ĐỘNG TRIGGER TOOL
# ---------------------------------------------------------
def chat_with_ai(user_input, messages_history):
    tools_schema = load_tools_schema()
    
    # Thêm câu hỏi của user vào lịch sử
    messages_history.append({"role": "user", "content": user_input})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": messages_history,
        "tools": tools_schema,
        "tool_choice": "auto",
        "temperature": 0.2
    }
    
    req = urllib.request.Request(API_URL, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            ai_msg = result['choices'][0]['message']
            
            # KIỂM TRA XEM AI CÓ MUỐN GỌI TOOL KHÔNG
            if ai_msg.get('tool_calls'):
                messages_history.append(ai_msg) # Lưu lại ý định gọi tool của AI
                
                for tool_call in ai_msg['tool_calls']:
                    func_name = tool_call['function']['name']
                    func_args = json.loads(tool_call['function']['arguments'])
                    
                    # Chạy hàm Python thật tương ứng
                    if func_name in AVAILABLE_TOOLS:
                        func_to_call = AVAILABLE_TOOLS[func_name]
                        function_response = func_to_call(**func_args)
                        
                        # Gửi kết quả của hàm trả lại cho AI
                        messages_history.append({
                            "role": "tool",
                            "name": func_name,
                            "tool_call_id": tool_call['id'],
                            "content": str(function_response)
                        })
                
                # Gọi lại AI lần 2 (Sau khi đã mớm kết quả Tool cho nó)
                return chat_with_ai_second_turn(messages_history)
            
            else:
                # Nếu AI trả lời bình thường (không cần tool)
                messages_history.append({"role": "assistant", "content": ai_msg['content']})
                return ai_msg['content']
                
    except Exception as e:
        print(f"Error calling API: {e}")
        return "ERROR"

def chat_with_ai_second_turn(messages_history):
    """Gọi lại AI sau khi đã có kết quả từ Tool"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }
    data = {
        "model": MODEL_NAME,
        "messages": messages_history,
        "temperature": 0.2
    }
    req = urllib.request.Request(API_URL, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            final_content = result['choices'][0]['message']['content']
            messages_history.append({"role": "assistant", "content": final_content})
            return final_content
    except Exception as e:
        return f"Error on second turn: {e}"

# ---------------------------------------------------------
# CHẠY THỬ
# ---------------------------------------------------------
if __name__ == "__main__":
    system_prompt = "Bạn là trợ lý VLearn. Hãy chủ động dùng tool nếu người dùng đề cập 'trang này' hoặc 'tài liệu'."
    history = [{"role": "system", "content": system_prompt}]
    
    print("--- DEMO AI FUNCTION CALLING (VLEARN) ---")
    print("Hãy thử gõ: 'Tóm tắt cho tôi nội dung đoạn này' hoặc 'Lưu lại khái niệm Hackathon nhé'")
    print("Gõ 'exit' để thoát.\n")
    
    while True:
        user_text = input("Học viên: ")
        if user_text.lower() == 'exit':
            break
            
        answer = chat_with_ai(user_text, history)
        print(f"\n🤖 AI: {answer}\n")
