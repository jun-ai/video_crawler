const cleanPlainText = (value) => {
  if (typeof value !== 'string') return ''
  return value.trim()
}

export const normalizeLookupInfo = (result = {}) => {
  const source = result && typeof result === 'object' ? result : {}
  const phonetic = cleanPlainText(source.phonetic).replace(/^\/+|\/+$/g, '').trim()
  const translation = cleanPlainText(source.translation) || cleanPlainText(source.meaning)
  const example = cleanPlainText(source.example)

  return { phonetic, translation, example }
}

export const buildMaterialOptions = (materials = []) => {
  return materials
    .filter((material) => material?.id !== null && material?.id !== undefined)
    .map((material) => ({
      value: material.id,
      label: cleanPlainText(material.title)
    }))
    .filter((option) => option.label)
}
