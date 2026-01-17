import colorsys

class color_utils:
  """
  Utility functions for color manipulation. This was generated with the help of generative AI (Claude 4.5 Sonnet)
  """
  
  def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
  def rgb_to_hex(rgb):
      return '#{:02x}{:02x}{:02x}'.format(
          int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
      )
  
  def desaturate(hex_color, saturation, value):
      r, g, b = color_utils.hex_to_rgb(hex_color)
      h, s, v = colorsys.rgb_to_hsv(r, g, b)
      s = s * saturation
      v = v * value
      r, g, b = colorsys.hsv_to_rgb(h, s, v)
      return color_utils.rgb_to_hex((r, g, b))