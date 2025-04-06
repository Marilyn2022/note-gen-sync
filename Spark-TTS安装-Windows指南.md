## **Spark-TTS安装（Windows指南）**

## 安装conda（如果还没有）

手动下载ZIP文件的步骤如下：

1. **访问下载链接**：打开浏览器，输入您要下载ZIP文件的链接地址。
2. **点击下载**：在网页上找到ZIP文件的下载按钮或链接，点击它。
3. **保存文件**：浏览器会弹出保存文件的对话框，选择保存的位置，然后点击“保存”。
4. **完成下载**：等待下载完成，然后在您选择的保存位置找到ZIP文件。

如果您需要更多具体的帮助，请提供更详细的信息！请提供您需要记录的内容或问题，我将直接为您回答。* 下载**[Miniconda](https://docs.conda.io/en/latest/miniconda.html)**并安装它。

* 确保在安装过程中检查**“添加conda到路径”**。

  ![2820c568-6536-4785-8772-84ef4f02ae9b.png](https://cdn.jsdelivr.net/gh//note-gen-image-sync@main/2820c568-6536-4785-8772-84ef4f02ae9b.png)

### **下载Spark-TTS**

您有**两个选项**来获取文件：

**选项1（建议用于Windows）：** **手动下载ZIP**

根据您的要求，您可以手动下载ZIP文件。请提供下载链接或相关信息，以便我能够帮助您获取所需的内容。好的，请问有什么具体的问题需要我回答吗？

* 去**[Spark-TTS github](https://github.com/SparkAudio/Spark-TTS)**
* 单击**“代码”>“下载zip”**，然后提取它。

**选项2：使用git（可选）**

* 如果您喜欢使用git，请安装**[git](https://git-scm.com/downloads)**并运行：
  ```shell
  git clone https://github.com/SparkAudio/Spark-TTS.git
  ```

---

## **2。创建一个Conda环境**

打开**命令提示（CMD）**并运行：

```shell
conda create -n sparktts python=3.12 -y
conda activate sparktts
```

这为Spark-TTS创建并激活了Python 3.12环境。

---

## **3。安装依赖项**

**在Spark-TTS文件夹**中（无论是从zip还是Git），运行：

```shell
pip install -r requirements.txt
```

---

## **4。安装Pytorch（自动检测CUDA或CPU）**

```shell
pip install torch torchvision torchaudio --index-url https://pytorch.org/get-started/previous-versions/

# OR Manually install a specific CUDA version (if needed)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # Older GPUs
```

---

## **5。下载模型**

有**两种**获取模型文件的方法。选择一个：

**选项1（建议）：使用Python在**spark-tts文件夹中
创建一个新文件，粘贴在内部，然后运行：**`download_model.py`**

```python
from huggingface_hub import snapshot_download
import os

# Set download path
model_dir = "pretrained_models/Spark-TTS-0.5B"

# Check if model already exists
if os.path.exists(model_dir) and len(os.listdir(model_dir)) > 0:
    print("Model files already exist. Skipping download.")
else:
    print("Downloading model files...")
    snapshot_download(
        repo_id="SparkAudio/Spark-TTS-0.5B",
        local_dir=model_dir,
        resume_download=True  # Resumes partial downloads
    )
    print("Download complete!")
```

运行它：

```shell
python download_model.py
```

✅**选项2：使用git（如果安装了）**

```shell
mkdir pretrained_models
git clone https://huggingface.co/SparkAudio/Spark-TTS-0.5B pretrained_models/Spark-TTS-0.5B
```

两种方法都可以使用 -**选择更容易的方法**。

---

## **6。运行Spark-TTS**

### **Web UI（推荐）**

对于**基于交互式浏览器的接口**，运行：

```shell
python webui.py
```

这将启动本地Web服务器，您可以在其中输入文本并生成语音或克隆语音。

---

## **7.故障排除和常见问题**

🔎**在寻求帮助之前，**
现有的讨论，文档或在线资源已经涵盖了许多常见问题。请：

* **搜索github问题首先**🕵️‍♂️
* **检查文档**📖
* **Google或使用AI工具（Chatgpt，DeepSeek等）**

如果您**仍然**需要帮助，请**说明您已经尝试过的内容，**以便我们更好地为您提供帮助！
