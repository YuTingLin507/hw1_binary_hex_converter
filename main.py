# 引用外部函式庫 (Library Imports)
# ipywidgets 是 Colab 環境專用的圖形元件庫。
# 將其簡稱為 'widgets'，用來建立畫面上看到的「文字輸入框(Text)」、「標籤(Label)」等物件。
import ipywidgets as widgets

# 從 IPython 的顯示模組中匯入兩個功能：
# 1. display: 用來將建立好的 UI 元件（如輸入框）實際「渲染」並顯示在網頁畫面上。
# 2. clear_output: 用來在更新轉換結果前，先擦除舊的訊息，避免畫面堆疊混亂。
from IPython.display import display, clear_output

# 不使用內建 int(s, base) 或 hex()) ---
# 設定字元字典,0-9=0-9, A=10, B=11, C=12, D=13, E=14, F=15, G=16, H=17, I=18, J=19
HEX_CHARS = "0123456789ABCDEFGHIJ"

def to_dec(s, base):
    #任意進位(2,10,16)轉十進位數字
    #【進位轉數字】
    #把「二進位的文字 10」讀成「真正的數量 2」。
    #原理：把目前的結果乘以基數，再加上新的位數。

    res = 0# 初始化結果變數，用來存放累加的總數值

    # 使用 for 迴圈逐一讀取字串中的每個字元 (例如 "101" 會依序讀取 '1', '0', '1')
    # strip() 去除前後空格，upper() 將英文字母統一轉大寫 (如 'a' 變 'A')
    for char in s.strip().upper():

        #透過字典找出該字元對應的數值 (例如 'A' 在字典中的索引是 10)
        digit = HEX_CHARS.find(char)

        #防呆：如果找不到字元 (digit為-1) 或數字超過該進位限制 (如2進位出現'2')，則跳出錯誤
        if digit == -1 or digit >= base: raise ValueError
        res = res * base + digit # 累加計算

    return res# 回傳最終計算出來的十進位整數

def from_dec(n, base):
    #將十進位數值轉換為目標進位 (2, 10, 16) 的字串
    #【數字轉進位】
    #把「數量 2」寫成「二進位文字 10」。
    #原理：不斷除以基數並取餘數，直到除完為止。

    # 如果數值剛好是 0，直接回傳字串 "0"，不需要進入下方的除法迴圈
    if n == 0:
      return "0"

    res = ""# 初始化結果字串，用來存放轉換後的文字 (如 "1010")
    while n > 0:

      # 1. 取得餘數：n 除以基數後的餘數 (例如 10 % 2 = 0)
      # 2. 查字典：將餘數轉換為對應的字元 (例如 10 變 'A')
      # 3. 字串拼接：將新取得的字元放在結果字串的「最前面」 (因為短除法要由下往上讀)
      res = HEX_CHARS[n % base] + res# 取得餘數並放在字串最前面

      # 取商數：將 n 除以基數並捨去小數點 (例如 10 // 2 = 5)，做為下一輪被除數
      n //= base
      
    return res# 回傳拼接完成的進位字串

# 圖形化介面 (UI) 與 邏輯綁定
# 建立三個文字輸入框物件，description 是標籤文字，placeholder 是框內的預設提示
bin_input = widgets.Text(description="2進位:", placeholder="例如: 100010")
v05_input = widgets.Text(description="5進位:", placeholder="例如:114")
dec_input = widgets.Text(description="10進位:", placeholder="例如: 34")
v15_input = widgets.Text(description="15進位:", placeholder="例如:24")
hex_input = widgets.Text(description="16進位:", placeholder="例如: 22")
v20_input = widgets.Text(description="20進位:", placeholder="例如:1E")

# widgets.Output 就像是一個「畫布」，讓我們可以把 print() 的內容顯示在特定的 UI 區塊中
# 建立一個輸出區域，用來顯示錯誤訊息 (如輸入錯誤字元)
error_out = widgets.Output()

# 將所有輸入框放進清單，方便後續大量處理
all_inputs = [bin_input, v05_input, dec_input, v15_input, hex_input, v20_input]
# 定義每個框對應的底數
base_map = {
    bin_input: 2, v05_input: 5, dec_input: 10, 
    v15_input: 15, hex_input: 16, v20_input: 20
}

# 同步轉換
def sync_all(change):
  #功能：當使用者在任一輸入框輸入文字時，自動計算並更新其他輸入框。
    # 檢查事件類型：只有當「數值(value)」發生「改變(change)」時才執行，避免處理不必要的系統訊號
    if change['type'] != 'change' or change['name'] != 'value': return
    
    # 取得當前操作的輸入框與其輸入內容
    # owner 代表「是哪一個輸入框被改動了」；val 代表「使用者輸入的新文字內容」
    owner = change['owner']
    val = change['new'].strip()
    
    #如果輸入框被清空了，則不執行後續的計算邏輯
    if not val: return

    # 在指定的輸出區域執行以下程式碼
    with error_out:
        clear_output()# 每次有新輸入，先清空之前的錯誤訊息 (保持畫面整潔)
        try:
            # 1. 取得來源框的底數並轉為十進位
            current_num = to_dec(val, base_map[owner])

            # 2. 防止「遞迴觸發」,暫時移除監聽，避免更新其他框時又觸發
            # 因為更新「其他框」的值也會觸發 change 事件，會導致程式陷入 A改B、B改C、C改A 的無限死迴圈。
            # 所以在更新別人之前，要先「暫時拔掉所有監聽器」。
            unobserve_all()
            
            # 3. 同步更新其他兩個輸入框的數值
            for ipt in all_inputs:
                if ipt != owner:
                    ipt.value = from_dec(current_num, base_map[ipt])# 如果目前操作的不是該進位框，就計算並更新該進位框的值

            #4. 更新完畢，恢復監聽
            observe_all()
        except:
          # 如果輸入了非法字元 (例如在2進位輸入2)，to_dec 會噴錯，這裡就會抓到並顯示提示
            print(f"⚠️ 輸入格式錯誤！")

# 監聽器控制
def observe_all():
  #為輸入框掛上監聽器：一旦 value 改變，就去執行 sync_all 函式
  for ipt in all_inputs:
        ipt.observe(sync_all, 'value')

def unobserve_all():
  #移除輸入框的監聽器：暫時中斷自動同步功能
  for ipt in all_inputs:
        ipt.unobserve(sync_all, 'value')

# 程式啟動入口
#初始化：啟動監聽器，讓輸入框具備「反應能力」
observe_all()

#使用 display 函式將 HTML 標題和三個輸入框、錯誤訊息區渲染到畫面上
display(widgets.HTML("<h3>🔄 多進位同步轉換器</h3>"), bin_input, v05_input, dec_input, v15_input, hex_input, v20_input,
    error_out)