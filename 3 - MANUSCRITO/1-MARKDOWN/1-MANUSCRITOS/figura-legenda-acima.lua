--[[
Filtro Pandoc para colocar legendas de figuras ACIMA da imagem.
Por padrão, Pandoc coloca a legenda embaixo.
Este filtro inverte a ordem para: legenda primeiro, depois imagem.
]]

local TARGET_WIDTH = os.getenv("FIG_WIDTH") or "80%"
local CAPTION_STYLE = os.getenv("FIG_CAPTION_STYLE") or "Legenda"

local function _get_inlines(block)
  return block.content or block.c
end

local function _caption_div_with_style(blocks)
  local normalized = {}

  for _, block in ipairs(blocks) do
    if block and block.t == "Plain" then
      table.insert(normalized, pandoc.Para(_get_inlines(block)))
    else
      table.insert(normalized, block)
    end
  end

  local attr = pandoc.Attr("", {}, { ["custom-style"] = CAPTION_STYLE })
  return pandoc.Div(normalized, attr)
end

local function parse_length(s)
  if type(s) ~= "string" then
    return nil
  end
  local num, unit = s:match("^%s*([0-9]+%.?[0-9]*)%s*([A-Za-z%%]+)%s*$")
  if not num or not unit then
    return nil
  end
  return tonumber(num), unit
end

function Image(img)
  -- Evita distorção por dupla restrição, mantendo a proporção
  if img.attr and img.attr.attributes then
    if img.attr.attributes["height"] ~= nil then
      img.attr.attributes["height"] = nil
    end

    local w = img.attr.attributes["width"]
    local n, u = parse_length(w)

    -- Normaliza apenas imagens claramente "full width" em polegadas ou centímetros
    -- mantendo imagens pequenas, mosaicos e esquemas sem mexer
    if w == "6.5in" or w == "6.50in" then
      img.attr.attributes["width"] = TARGET_WIDTH
    elseif n and u == "in" and n >= 6.0 then
      img.attr.attributes["width"] = TARGET_WIDTH
    elseif n and u == "cm" and n >= 15.0 then
      img.attr.attributes["width"] = TARGET_WIDTH
    end
  end
  return img
end

function Figure(fig)
  -- Move a legenda para cima preservando o Figure original (attr/id).
  -- Em Pandoc 3.x, fig.caption.long é uma lista de Blocks.

  local result = {}

  if fig.caption and fig.caption.long and #fig.caption.long > 0 then
    table.insert(result, _caption_div_with_style(fig.caption.long))
  end

  -- Remove a legenda do Figure para evitar duplicação (em geral o DOCX coloca abaixo)
  fig.caption = pandoc.Caption()
  table.insert(result, fig)

  return result
end
