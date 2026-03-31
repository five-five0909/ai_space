import re
import os

input_file = r'd:\Desktop\anki卡片制作\管理类综合\管理类综合公式背诵.txt'
output_file = r'd:\Desktop\anki卡片制作\管理类综合\管理类综合公式背诵_优化版.txt'

hints = {
    "质数性质": "💡 <b>易错点</b>：2既是唯一的偶质数，也是最小的质数；1既不是质数也不是合数。",
    "奇偶重要结论": "💡 <b>考点</b>：常用于判断方程是否有整数解、或者求解不定方程中的奇偶数配对。",
    "循环小数化分数": "📝 <b>记忆技巧</b>：分母对应循环位填9，不循环位填0；分子是整个小数减去不循环部分。",
    "整除特征": "💡 <b>考点</b>：能被11整除常通过奇偶位数字和之差检验；能被7,11,13整除也常结合三位截断法。",
    "比的基本性质": "💡 <b>方法提示</b>：遇到连比公式 $x:y:z = a:b:c$，常设一份为 $k$ 来统一表示 $x, y, z$。",
    "比例定理": "💡 <b>核心技巧</b>：等比定理在各项分母之和不为0时非常有用，常用于填空或面积比例。",
    "绝对值基本不等式": "🎯 <b>解题策略</b>：「大于取两边，小于取中间」。这是去绝对值符号最核心的步骤！",
    "绝对值性质": "💡 <b>考点</b>：自比性 $|a| \\ge \\pm a$ 常用于根式化简与极值求解。非负性常考多个非负数之和为0。",
    "变化率公式": "⚠️ <b>注意</b>：分母永远是「原值」或「基准值」。甲比乙大 $p\\%$ 不等价于乙比甲小 $p\\%$。",
    "工程问题核心公式": "💡 <b>解题方法</b>：常将总工程量设为「1」或「几个时间的最小公倍数」以消除分数计算。",
    "路程问题基本公式": "💡 <b>比例应用</b>：时间相同找速度比=路程比；速度相同找时间比=路程比，非常高效。",
    "交叉法": "💡 <b>适用场景</b>：已知两部分各自的平均指标及其混合后的整体平均指标，求两部分数量比。",
    "浓度不变准则": "📝 <b>核心准则</b>：无论怎么倒，只要不加水和溶质，溶液只要混合均匀，其浓度与原杯相同。",
    "三个集合公式（宏观）": "💡 <b>韦恩图法</b>：解三个集合的题目，画韦恩图往里填数字是最直观、最稳妥的方法！",
    "因式定理": "💡 <b>核心</b>：令除数的一次式等于0求出 $x$ 值代入被除式；若结果等于0则能整除。",
    "一元二次函数性质": "📐 <b>数形结合</b>：所有涉及一元二次的最值或根的分布问题，必须画出抛物线开口和对称轴！",
    "对数运算性质": "💡 <b>运算技巧</b>：化同底是核心。利用换底公式可将不同底对数转化为同底以进行乘除运算。",
    "二项式系数性质": "💡 <b>考点</b>：常考中间项最大值；注意区分「项的系数」与「二项式系数（组合数）」的本质区别。",
    "一元二次方程判别式": "⚠️ <b>细节</b>：方程有两个实根是指 $\\Delta \\ge 0$，两个不相等的实根才是 $\\Delta > 0$。",
    "韦达定理": "💡 <b>常见变形</b>：$|x_1-x_2| = \\sqrt{(x_1+x_2)^2 - 4x_1x_2}$ 是极高频的考点形式。",
    "实根分布（两正根）": "📐 <b>思路</b>：画图！开口向上时，对称轴必须在 $y$ 轴右侧，且与 $y$ 轴交点为正，再满足 $\\Delta \\ge 0$。",
    "绝对值不等式 |f(x)|<|g(x)|": "💡 <b>神仙解法</b>：两边均为正，直接两边平方移项化简，用平方差公式转为一次或二次不等式。",
    "高次不等式穿针引线法": "💡 <b>口诀</b>：奇次根穿过，偶次根不穿过（奇穿偶不穿，从右上开始穿）。",
    "柯西不等式": "💡 <b>特征</b>：通常在遇到平方和（$x^2+y^2$）与一次积（$ax+by$）相互转化时使用。",
    "均值不等式": "💡 <b>使用条件</b>：一正、二定、三相等。遇到倒数和（如 $\\frac{b}{a} + \\frac{a}{b}$）常用均值不等式。",
    "等差数列判定方法": "📝 <b>速判技巧</b>：如果通项 $a_n = pn+q$ 或 前 $n$ 项和 $S_n = An^2+Bn$ （无常数！），必为等差数列。",
    "等差数列前n项和最值": "🎯 <b>解法</b>：首选找 $a_n$ 与 $a_{n+1}$ 变号的临界处 $a_n \\ge 0, a_{n+1} \\le 0$，其次可选二次函数求顶点。",
    "等比数列判定方法": "📝 <b>速判技巧</b>：如果前 $n$ 项和是 $S_n = A - A q^n$（底数幂为 $n$ 且系数互为相反数），必为等比数列。",
    "角平分线性质": "📐 <b>辅助线</b>：遇到角平分线常向两边作垂线，或在角两边截取相等的线段构造全等三角形。",
    "三角形面积公式": "💡 <b>面积转换</b>：同高不同底，面积比等于底之比，这是解决阴影部分面积最常用的核心性质。",
    "三角形重心": "📐 <b>重心性质</b>：重心到顶点的距离等于到对边中点距离的2倍。",
    "三角形的内心": "💡 <b>应用</b>：内心到三边距离就是内切圆半径 $r$，结合面积公式 $S=\\frac{1}{2}(a+b+c)r$ 非常好用。",
    "三角形的全等判定": "⚠️ <b>注意</b>：不要误认为 SSA（两边及一边的对角）能判定全等，这是考试中最常见的陷阱。",
    "燕尾定理": "💡 <b>应用模型</b>：处理不规则四边形和多线交点中的面积比例问题非常强大。",
    "中线长公式": "📐 <b>等价作法</b>：经常通过“延长中线一倍”构造平行四边形，用对角线平方和定理求解。",
    "直角三角形30°角性质": "💡 <b>逆向思维</b>：如果测出一条直角边刚好等于斜边一半，那它的对角必然是30°。",
    "直角三角形内切圆半径": "📝 <b>速算公式</b>：考频极高！$r = \\frac{a+b-c}{2}$ 必须牢记在心。",
    "等腰直角三角形": "📐 <b>考点</b>：常与圆内接多边形、扇形结合出现，只要遇到，立刻标注边长比例 $1:1:\\sqrt{2}$。",
    "等边三角形": "💡 <b>重点公式</b>：极高频，记住面积 $\\frac{\\sqrt{3}}{4}a^2$，高 $\\frac{\\sqrt{3}}{2}a$ 会节省大量计算时间。",
    "任意四边形蝴蝶定理": "🦋 <b>口诀</b>：对角面积相乘积相等（$S_1 S_3 = S_2 S_4$）。若是梯形，还能推得比值。",
    "圆周角定理": "⭕ <b>圆的核心</b>：直径必有90°圆周角；有90°圆周角则必跨直径。找直角首选这个！",
    "平行线距离": "📏 <b>注意点</b>：用公式 $d = \\frac{|C_1-C_2|}{\\sqrt{A^2+B^2}}$ 前，必须先确保两条直线的 $A$ 和 $B$ 系数完全一致！",
    "直线与圆的位置关系": "💡 <b>核心判别法</b>：永远用「圆心到直线距离 $d$ 与半径 $r$ 的长短关系」判别，切勿联立方程计算判别式（计算极其繁琐）。",
    "圆上一点切线方程": "🔥 <b>秒杀技巧</b>：圆心在原点时，公式为 $x_0 x + y_0 y = r^2$。只需把切点坐标代入原方程一半即可！",
    "乘法原理": "💡 <b>逻辑界定</b>：每一步都必须做完才能完成这件事，就用乘法；只要做一步就算完成一类情况，就用加法。",
    "打包问题（相邻）": "📝 <b>核心步骤</b>：必须相邻的元素整体“打包”当作1个元素，排完后千万别忘了包内元素还要“内部互排”。",
    "插孔问题（不相邻）": "📝 <b>核心步骤</b>：先把没有要求的元素排好队，再把要求“不相邻”的元素一个一个插进产生的空隙中。",
    "插板问题": "💡 <b>应用前提</b>：分发的元素必须“完全一样”，每个接受方“至少分1个”。如果包含分0个，先借虚拟元素再插板。",
    "错排问题": "📝 <b>速记数值</b>：元素个数 $n$ 与全错排数 $D_n$ 的对应 $n=1\\to 0, n=2\\to 1, n=3\\to 2, n=4\\to 9, n=5\\to 44$。",
    "古典概型": "🎲 <b>本质</b>：所求事件方法数 $\\div$ 总方法数。解题本质其实就是做两次排列组合或计数。",
    "方差": "💡 <b>平移缩放性质</b>：若所有数据同加常数 $c$，方差不变；若所有数据同乘 $k$，方差变为变为 $k^2$ 倍。",
}

out_lines = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            tag = parts[0]
            front = parts[1]
            back = "\t".join(parts[2:]) # just in case back contained tabs initially
            
            # --- FRONT FORMATTING ---
            # Remove full bold and make only 【...】 bold
            front = re.sub(r'<b>(【.*?】)(.*?)</b>', r'<b>\1</b> \2', front)
            
            # --- BACK FORMATTING ---
            # Extract box
            match = re.search(r'<div class="(latex-box box-[^"]+)">(.*?)</div>', back, re.IGNORECASE | re.DOTALL)
            if match:
                box_class = match.group(1)
                content = match.group(2)
                
                # MathJax conversions: \( \) -> $ $
                content = content.replace(r'\(', '$').replace(r'\)', '$')
                content = content.replace(r'\[', '$$').replace(r'\]', '$$')
                
                # List formatting for <br> (if no ul already)
                if '<ul>' not in content and '<br>' in content:
                    items = [it.strip() for it in re.split(r'<br\s*/?>', content) if it.strip()]
                    if len(items) > 1:
                        # Check if first item is just a short intro (no colon, short)
                        if ('：' not in items[0] and ':' not in items[0] and len(items[0]) < 25):
                            list_html = '<ul>' + ''.join([f'<li>{it}</li>' for it in items[1:]]) + '</ul>'
                            content = items[0] + '<br>' + list_html
                        else:
                            content = '<ul>' + ''.join([f'<li>{it}</li>' for it in items]) + '</ul>'
                
                # Bold terms before colon
                def bold_term(m):
                    term = m.group(1)
                    if '<' in term or '$' in term:
                        return m.group(0)
                    return f'<b>{term}</b>：'
                content = re.sub(r'([^<>\s：；。，$]{1,12})[：:]', bold_term, content)
                
                # Final Back assembled
                new_back = f'<div class="{box_class}">{content}</div>'
                
                # Determine hint
                hint_added = False
                for k, hint_text in hints.items():
                    if k in tag or k in front:
                        # Add brilliant Notion-style callout box
                        callout = f'<div style="margin-top: 15px; background: #fdf6e3; padding: 12px; border-radius: 6px; border-left: 4px solid #f39c12; font-size: 0.95em; color: #5c5a54; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' + hint_text + '</div>'
                        new_back += callout
                        hint_added = True
                        break # Add only first matching hint
                
                # Assign back
                back = new_back

            out_lines.append(f"{tag}\t{front}\t{back}")
        else:
            out_lines.append(line)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print(f"Successfully processed and wrote {len(out_lines)} optimal Anki cards to {output_file}.")
