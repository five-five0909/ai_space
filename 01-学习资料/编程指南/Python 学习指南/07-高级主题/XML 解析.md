# XML 解析

Python 提供多种 XML 解析方式。

## ElementTree (推荐)

```python
import xml.etree.ElementTree as ET

# 解析 XML 字符串
xml_str = '<root><item id="1">内容</item></root>'
root = ET.fromstring(xml_str)

# 解析文件
tree = ET.parse('data.xml')
root = tree.getroot()

# 访问元素
print(root.tag)           # 'root'
print(root.attrib)        # {}

# 查找子元素
for item in root.findall('item'):
    print(item.get('id'))     # '1'
    print(item.text)          # '内容'
```

## XPath 查询

```python
# 查找所有 item
items = root.findall('.//item')

# 查找特定属性
special_items = root.findall('.//item[@id="1"]')

# 查找嵌套元素
nested = root.findall('.//category/item')
```

## 科研实战场景

### 1. 解析配置文件

```python
def parse_experiment_config(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    config = {
        'model': root.find('model').text,
        'learning_rate': float(root.find('lr').text),
        'epochs': int(root.find('epochs').text),
        'data_dir': root.find('data').get('path')
    }
    return config
```

### 2. 解析 PASCAL VOC 标注

```python
def parse_voc_annotation(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    annotation = {
        'filename': root.find('filename').text,
        'size': {
            'width': int(root.find('size/width').text),
            'height': int(root.find('size/height').text),
        },
        'objects': []
    }

    for obj in root.findall('object'):
        annotation['objects'].append({
            'name': obj.find('name').text,
            'bbox': {
                'xmin': int(obj.find('bndbox/xmin').text),
                'xmax': int(obj.find('bndbox/xmax').text),
                'ymin': int(obj.find('bndbox/ymin').text),
                'ymax': int(obj.find('bndbox/ymax').text)
            }
        })
    return annotation
```

## 性能提示

- ElementTree 适合大多数场景
- lxml 功能更强但需要安装
- 大文件使用 iterparse 流式解析

```python
for event, elem in ET.iterparse('large.xml', events=('end',)):
    if elem.tag == 'item':
        process(elem)
        elem.clear()  # 释放内存
```
