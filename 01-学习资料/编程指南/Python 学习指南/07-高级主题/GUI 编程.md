# GUI 编程

## 快速原型：Gradio

```python
import gradio as gr

def predict(text: str) -> str:
    return text.upper()

demo = gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
    title="文本转换器"
)

demo.launch()
```

### Gradio 多输入多输出

```python
def process(text: str, temperature: float, max_tokens: int):
    result = f"处理：{text}, temp={temperature}"
    return result, {"status": "success"}

demo = gr.Interface(
    fn=process,
    inputs=[
        gr.Textbox(label="输入文本"),
        gr.Slider(0, 1, label="Temperature"),
        gr.Number(label="Max Tokens")
    ],
    outputs=[gr.Textbox(label="结果"), gr.JSON(label="状态")]
)
```

## Streamlit - 数据应用

```python
import streamlit as st
import pandas as pd

st.title("实验结果可视化")

model = st.sidebar.selectbox("选择模型", ["ResNet50", "VGG16"])

@st.cache_data
def load_data():
    return pd.read_csv("results.csv")

df = load_data()
st.line_chart(df.set_index("epoch")["loss"])
st.metric("Best Accuracy", df["accuracy"].max())
```

## 科研实战场景

### 1. 模型推理演示

```python
import gradio as gr
import torch

model = None

def load_model():
    global model
    model = torch.load("best_model.pt")
    model.eval()

def predict(image):
    if model is None:
        load_model()
    return {"类别": "dog", "置信度": 0.95}

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=3),
    examples=["example1.jpg", "example2.jpg"]
)
demo.launch()
```

### 2. 超参数搜索工具

```python
import gradio as gr

def run_experiment(lr, batch_size, epochs, optimizer):
    return {"final_loss": 0.1, "final_acc": 0.9}

with gr.Blocks() as demo:
    gr.Markdown("# 超参数搜索工具")
    lr = gr.Slider(1e-5, 1e-2, label="Learning Rate")
    batch = gr.Dropdown([16, 32, 64], label="Batch Size")
    btn = gr.Button("运行实验")
    output = gr.JSON(label="结果")
    btn.click(run_experiment, [lr, batch], output)

demo.launch()
```

## Gradio vs Streamlit

| 特性 | Gradio | Streamlit |
|------|--------|-----------|
| 定位 | 快速 ML 演示 | 数据应用 |
| 学习曲线 | 低 | 低 |
| 适合场景 | 模型演示 | 数据看板 |
