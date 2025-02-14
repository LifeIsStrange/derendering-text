import skia
import random
import numpy as np
import math

def get_paint(effect_params):
    shadow_param, fill_param, grad_param, stroke_param = effect_params
    fill_paint = get_fill_paint(fill_param)
    shadow_paint = get_shadow_paint(shadow_param)
    stroke_paint = get_stroke_paint(stroke_param)
    if grad_param is not None:
        grad_paint = get_gradation_paint(grad_param)
    else:
        grad_paint = None
    return shadow_paint,fill_paint, stroke_paint, grad_paint

def get_alpha(mask_size, textblob, offsets, effect_params, paints, angle=0):
    height, width = mask_size
    offset_y, offset_x = offsets
    shadow_param, fill_param, grad_param, stroke_param = effect_params
    shadow_paint, fill_paint, grad_paint, stroke_paint = paints
    fill_alpha = get_fill_alpha(height, width, textblob, offset_x, offset_y, angle)
    stroke_alpha = get_stroke_alpha(height, width, textblob, offset_x, offset_y, stroke_param, angle)
    shadow_bitmap, shadow_alpha = get_shadow_bitmap_and_alpha(height, width, shadow_param, fill_alpha, shadow_paint)
    return shadow_alpha, fill_alpha, stroke_alpha, shadow_bitmap

def alpha_with_visibility(alpha, visibility_flags):
    fill_alpha,shadow_alpha,stroke_alpha,shadow_bitmap = alpha
    shadow_visibility_flag, fill_visibility_flag, gardation_visibility_flag, stroke_visibility_flag = visibility_flags
    if fill_visibility_flag==False:
        shadow_alpha = np.zeros_like(fill_alpha)
    if shadow_visibility_flag==False:
        fill_alpha = np.zeros_like(fill_alpha)
    if stroke_visibility_flag==False:
        stroke_alpha = np.zeros_like(fill_alpha)
    return shadow_alpha,fill_alpha,stroke_alpha,shadow_bitmap

def get_canvas(height, width, img = None):
    surface = skia.Surface(width, height)
    canvas = surface.getCanvas()
    if img is not None:
        tmp=np.zeros((height, width,4)).astype(dtype=np.uint8)+255
        tmp[:,:,0:3]=img.copy()
        image = skia.Image.fromarray(tmp)
        canvas.drawImage(image,0,0)
    else:
        canvas.clear(skia.ColorSetRGB(0, 0, 0))
    return surface, canvas

def get_fill_param():
    if random.random()<0.2:
        val = random.randint(230,255)
        fill_color = [val,val,val]
    elif random.random()<0.4:
        val = random.randint(0,50)
        fill_color = [val,val,val]
    else:
        fill_color = [random.randint(0,255),random.randint(0,255),random.randint(0,255)]
    fill_param = fill_color
    return fill_param
def get_gradation_param(x_start,y_start,text_width,text_height):
    def n(v,minv=0):
        return max(int(v),minv)
    x_start,y_start,text_width,text_height = n(x_start),n(y_start),n(text_width,1),n(text_height,1)
    if random.random()<0.:
        points = [[x_start, 0], [x_start+text_width, 0]]
    elif random.random()<0.:
        points = [[0, y_start], [0, y_start+text_height]]
    else:
        points = [[random.randint(x_start,x_start+text_width), random.randint(y_start,y_start+text_height)], 
                  [random.randint(x_start,x_start+text_width), random.randint(y_start,y_start+text_height)]]
    if random.random()<0.5:
        if random.random()<0.5:
            start = random.randint(0,55)
            end = random.randint(200,255)
        else:
            start = random.randint(200,255)
            end = random.randint(0,55)
        colors = [[start,start,start], [end,end,end]]
    else:
        colors = [[random.randint(0,255),random.randint(0,255),random.randint(0,255)], [random.randint(0,255),random.randint(0,255),random.randint(0,255)]]
    c0 = random.random()*0.5
    c1 = c0 + (1-c0)*random.random()# < 1
    cstop = [c0,c1]
    grad_param = (points, colors, cstop)
    return grad_param
def get_stroke_param(size_param):
    stroke_size_rate = random.random()*0.04 + 0.01
    stroke_size = size_param*stroke_size_rate
    if random.random()<0.2:
        val = random.randint(230,255)
        stroke_color = [val,val,val]
    elif random.random()<0.4:
        val = random.randint(0,50)
        stroke_color = [val,val,val]
    else:
        stroke_color=[random.randint(0,255),random.randint(0,255),random.randint(0,255)]
    stroke_param = stroke_size, stroke_color
    return stroke_param
def get_shadow_param(size_param):
    if random.random()<0.25:
        bsz = size_param*random.random()*0.25
    else:
        bsz = 0
    r = random.random()
    if r<0.1:
        dp = size_param*random.random()*0.25
    elif r<0.2:
        dp = size_param*random.random()*0.1
    else:
        dp = 0
    
    theta = np.pi * 2*random.random()
    if (random.random()<0.25):
        shift = size_param*(random.random()*0.2+0.05)
    else:
        shift = size_param*(random.random()*0.05 + 0.02)
    # shadow shift:
    offsetds_y = int(-math.sin(theta)*shift)
    offsetds_x = int(math.cos(theta)*shift)
    if random.random()<0.25:
        op = 0.5+random.random()*0.5
    else:
        op = 1.
    if random.random()<0.2:
        val = random.randint(230,255)
        shadow_color = [val,val,val]
    elif random.random()<0.4:
        val = random.randint(0,50)
        shadow_color = [val,val,val]
    else:
        shadow_color=[random.randint(0,255),random.randint(0,255),random.randint(0,255)]
    shadow_param = (op,bsz,dp,theta,shift,offsetds_y,offsetds_x,shadow_color)
    return shadow_param
def get_fill_paint(fill_param):
    fill_color = fill_param
    fill_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.ColorSetRGB(fill_color[0], fill_color[1], fill_color[2]),
        Style=skia.Paint.kFill_Style,
    )
    return fill_paint
def get_gradation_paint(grad_param):
    points, colors, cstop = grad_param
    points = [skia.Point(points[0][0], points[0][1]), skia.Point(points[1][0], points[1][1])]
    colors = [skia.ColorSetRGB(colors[0][0],colors[0][1],colors[0][2]), skia.ColorSetRGB(colors[1][0],colors[1][1],colors[1][2])]
    p_grad = skia.Paint(
        AntiAlias=True,
    )
    p_grad.setShader(skia.GradientShader.MakeLinear(points, colors, cstop))
    return p_grad

def get_stroke_paint(stroke_param):
    stroke_width, stroke_color = stroke_param
    stroke_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.ColorSetRGB(stroke_color[0], stroke_color[1], stroke_color[2]),
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=stroke_width,
    )
    return stroke_paint
def get_shadow_paint(shadow_param):
    (op,bsz,dp,theta,shift,offsetds_y,offsetds_x,shadow_color) = shadow_param
    shadow_paint = skia.Paint()
    shadow_paint.setAntiAlias(True)
    colorMatrix = [
        0, 0, 0, 0, 1,
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0,
        0, 0, 0, 1, 0
    ]
    colorMatrix[4::5] = (shadow_color[0] /
                         255., shadow_color[1] /
                         255., shadow_color[2] /
                         255., 0)
    cf = skia.ColorFilters.Matrix(colorMatrix)
    color = skia.ColorFilterImageFilter.Make(cf)
    #dp = 0
    dilateparam_x, dilateparam_y = dp, dp
    sigmax, sigmay = bsz, bsz
    dilate = skia.DilateImageFilter.Make(dilateparam_x, dilateparam_y, color)
    blur = skia.BlurImageFilter.Make(sigmax / 2., sigmay / 2., color)
    blur_dilate = skia.BlurImageFilter.Make(sigmax / 2., sigmay / 2., dilate)
    shadow_paint.setImageFilter(blur_dilate)
    shadow_paint.setBlendMode(skia.BlendMode.kSrcOver)
    return shadow_paint

def get_shadow_bitmap_and_alpha(height, width, shadow_param, fill_alpha, shadow_paint):
    surface, canvas = get_canvas(height, width)
    (op,bsz,dp,theta,shift,offsetds_y,offsetds_x,shadow_color) = shadow_param
    shadow_alpha = (fill_alpha.copy().astype(np.float32)).astype(np.uint8)
    shadow_bitmap = skia.Bitmap()
    assert shadow_bitmap.tryAllocPixels(skia.ImageInfo.MakeA8(width, height))
    shadow_array = np.array(shadow_bitmap, copy=False)
    shadow_array[:, :] = shadow_alpha * op
    # keep alpha
    shadow_paint.setBlendMode(skia.BlendMode.kSrc)
    canvas.drawBitmap(
        shadow_bitmap,
        offsetds_x,
        offsetds_y,
        shadow_paint)
    shadow_alpha = surface.makeImageSnapshot().toarray()[:, :, 3]
    if offsetds_y > 0:
        shadow_alpha[0:offsetds_y, :] = 0
    else:
        shadow_alpha[height + offsetds_y:, :] = 0
    if offsetds_x > 0:
        shadow_alpha[:, 0:offsetds_x] = 0
    else:
        shadow_alpha[:, width + offsetds_x:] = 0
    return shadow_bitmap, shadow_alpha
def get_stroke_alpha(height, width, textblob, offset_x, offset_y, stroke_param,angle,width_scale=1):
    surface, canvas = get_canvas(height, width)
    stroke_width, stroke_color = stroke_param
    stroke_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.ColorSetRGB(255, 0, 0),
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=stroke_width,
    )
    canvas.rotate(angle)
    canvas.scale(width_scale, 1)
    canvas.drawTextBlob(textblob, offset_x, offset_y, stroke_paint)
    canvas.resetMatrix()
    stroke_alpha = surface.makeImageSnapshot().toarray()[:, :, 2]
    return stroke_alpha
def get_fill_alpha(height,width, textblob, offset_x, offset_y,angle,width_scale=1):
    surface, canvas = get_canvas(height,width)
    fill_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.ColorSetRGB(255, 0, 0),
        Style=skia.Paint.kFill_Style,
    )
    canvas.rotate(angle)
    canvas.scale(width_scale, 1)
    canvas.drawTextBlob(textblob, offset_x, offset_y, fill_paint)
    canvas.resetMatrix()
    fill_alpha = surface.makeImageSnapshot().toarray()[:, :, 2]
    return fill_alpha
def render_fill(canvas, textblob, offset_x, offset_y, fill_paint):
    fill_paint.setBlendMode(skia.BlendMode.kSrcOver)
    canvas.drawTextBlob(textblob, offset_x, offset_y, fill_paint)
    return canvas
def render_bitmap(canvas, paint, target_bitmap, offset_x=0, offset_y=0):
    paint.setBlendMode(skia.BlendMode.kSrcOver)
    canvas.drawBitmap(
        target_bitmap,
        int(offset_x),
        int(offset_y),
        paint)
    return canvas
def render_stroke(canvas, textblob, offset_x, offset_y, stroke_paint):
    stroke_paint.setBlendMode(skia.BlendMode.kSrcOver)
    canvas.drawTextBlob(textblob, offset_x, offset_y, stroke_paint)
    return canvas

def render_gradation(canvas, textblob, offset_x, offset_y, grad_paint):
    grad_paint.setBlendMode(skia.BlendMode.kOverlay)
    grad_paint.setAlphaf(1)
    canvas.drawTextBlob(textblob, offset_x, offset_y, grad_paint)
    return canvas

def alpha2bitmap(height, width, alpha, op=1.0):
    surface, canvas = get_canvas(height, width)
    tmp_bitmap = skia.Bitmap()
    assert tmp_bitmap.tryAllocPixels(skia.ImageInfo.MakeA8(width, height))
    tmp_array = np.array(tmp_bitmap, copy=False)
    tmp_array[:, :] = alpha * op
    return tmp_bitmap

def get_visibility_flag():
    if random.random() > 0.5:
        shadow_flag=True
    else:
        shadow_flag=False
    if random.random() > 0.5:
        stroke_flag=True
    else:
        stroke_flag=False
    if (shadow_flag==True or stroke_flag==True) and random.random() > 0.95:
        fill_flag=False
    else:
        fill_flag=True

    if fill_flag==True and random.random() < 0.1:
        gradtion_flag=True
    else:
        gradtion_flag=False

    return [fill_flag, shadow_flag, stroke_flag, gradtion_flag]