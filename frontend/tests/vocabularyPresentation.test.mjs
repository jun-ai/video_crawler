import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildMaterialOptions,
  normalizeLookupInfo
} from '../src/lib/vocabularyPresentation.js'

test('normalizeLookupInfo removes duplicate phonetic wrappers and keeps plain text fields', () => {
  assert.deepEqual(
    normalizeLookupInfo({
      phonetic: '//əˈkaʊntəbəl//',
      translation: '  adj. 负有责任的  ',
      example: '  We are accountable for the result.  '
    }),
    {
      phonetic: 'əˈkaʊntəbəl',
      translation: 'adj. 负有责任的',
      example: 'We are accountable for the result.'
    }
  )
})

test('normalizeLookupInfo rejects object-shaped API leakage and falls back to meaning', () => {
  assert.deepEqual(
    normalizeLookupInfo({
      phonetic: null,
      translation: { normal_word: 'leaked schema' },
      meaning: '正常释义',
      example: ['not', 'plain text']
    }),
    {
      phonetic: '',
      translation: '正常释义',
      example: ''
    }
  )
})

test('normalizeLookupInfo handles a null API payload', () => {
  assert.deepEqual(normalizeLookupInfo(null), {
    phonetic: '',
    translation: '',
    example: ''
  })
})

test('buildMaterialOptions keeps searchable material titles only', () => {
  assert.deepEqual(
    buildMaterialOptions([
      { id: 2, title: '  洛杉矶最佳餐饮地点  ' },
      { id: 3, title: '' },
      { id: null, title: '无效语料' },
      { id: 4, title: '我的一周饮食与训练' }
    ]),
    [
      { value: 2, label: '洛杉矶最佳餐饮地点' },
      { value: 4, label: '我的一周饮食与训练' }
    ]
  )
})
