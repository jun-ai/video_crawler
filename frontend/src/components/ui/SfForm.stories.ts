import type { Meta, StoryObj } from '@storybook/vue3'
import { ref, reactive } from 'vue'
import SfForm from './SfForm.vue'
import SfFormItem from './SfFormItem.vue'
import SfInput from './SfInput.vue'
import SfButton from './SfButton.vue'
import { User, Mail } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfForm',
  component: SfForm,
  tags: ['autodocs'],
  argTypes: {}
} satisfies Meta<typeof SfForm>

export default meta
type Story = StoryObj<typeof meta>

export const Basic: Story = {
  name: '基础表单',
  render: () => ({
    components: { SfForm, SfFormItem, SfInput, SfButton, User, Mail },
    setup() {
      const form = reactive({ name: '', email: '' })
      const submitted = ref<null | { name: string; email: string }>(null)
      function onSubmit() {
        submitted.value = { ...form }
      }
      return { form, submitted, onSubmit }
    },
    template: `
      <div style="max-width: 420px;">
        <SfForm @submit="onSubmit">
          <SfFormItem label="姓名" required>
            <SfInput v-model="form.name" placeholder="输入姓名">
              <template #prefix><User :size="14" /></template>
            </SfInput>
          </SfFormItem>
          <SfFormItem label="邮箱" required>
            <SfInput v-model="form.email" type="email" placeholder="you@example.com">
              <template #prefix><Mail :size="14" /></template>
            </SfInput>
          </SfFormItem>
          <SfButton type="primary" html-type="submit">提交</SfButton>
        </SfForm>

        <div v-if="submitted" style="margin-top: 20px; padding: 12px; border-radius: 8px; background: var(--color-bg-elevated); font-size: 13px;">
          已提交：{{ submitted }}
        </div>
      </div>
    `
  })
}

export const WithValidation: Story = {
  name: '带校验',
  render: () => ({
    components: { SfForm, SfFormItem, SfInput, SfButton, User, Mail },
    setup() {
      const form = reactive({ name: '', email: '', password: '' })
      const errors = reactive<{ name: string; email: string; password: string }>({
        name: '', email: '', password: ''
      })
      const passed = ref(false)

      function validate() {
        errors.name = form.name.trim() ? '' : '姓名至少 2 个字'
        const emailOk = /^[\w.+-]+@[\w-]+\.[\w.-]+$/.test(form.email)
        errors.email = emailOk ? '' : '邮箱格式不对'
        errors.password = form.password.length >= 6 ? '' : '密码至少 6 位'
        passed.value = !errors.name && !errors.email && !errors.password
      }

      function onSubmit() {
        validate()
        if (passed.value) {
          alert('提交成功：' + JSON.stringify(form))
        }
      }

      return { form, errors, passed, onSubmit, validate }
    },
    template: `
      <div style="max-width: 420px;">
        <SfForm @submit="onSubmit">
          <SfFormItem label="姓名" required :error="errors.name">
            <SfInput v-model="form.name" placeholder="输入姓名" @blur="validate" />
          </SfFormItem>
          <SfFormItem label="邮箱" required :error="errors.email">
            <SfInput v-model="form.email" type="email" placeholder="you@example.com" @blur="validate" />
          </SfFormItem>
          <SfFormItem label="密码" required :error="errors.password">
            <SfInput v-model="form.password" type="password" placeholder="至少 6 位" @blur="validate" />
          </SfFormItem>
          <div style="display: flex; gap: 8px;">
            <SfButton type="primary" html-type="submit">提交</SfButton>
            <SfButton type="default" @click="validate">仅校验</SfButton>
          </div>
        </SfForm>
      </div>
    `
  })
}

export const HorizontalLayout: Story = {
  name: '水平布局',
  render: () => ({
    components: { SfForm, SfFormItem, SfInput, SfButton, User, Mail },
    setup() {
      const form = reactive({ name: '', email: '' })
      return { form }
    },
    template: `
      <style>
        .sf-form--horizontal .sf-form-item {
          display: grid;
          grid-template-columns: 100px 1fr;
          align-items: center;
          gap: 16px;
        }
        .sf-form--horizontal .sf-form-label {
          text-align: right;
        }
      </style>
      <div style="max-width: 600px;">
        <SfForm class="sf-form--horizontal" @submit="() => alert('submit')">
          <SfFormItem label="姓名" required>
            <SfInput v-model="form.name" placeholder="输入姓名" />
          </SfFormItem>
          <SfFormItem label="邮箱" required>
            <SfInput v-model="form.email" type="email" placeholder="you@example.com" />
          </SfFormItem>
          <div style="display: flex; gap: 8px; padding-left: 116px;">
            <SfButton type="primary" html-type="submit">提交</SfButton>
            <SfButton type="default">取消</SfButton>
          </div>
        </SfForm>
      </div>
    `
  })
}

export const WithFormItems: Story = {
  name: '与 FormItem 组合',
  render: () => ({
    components: { SfForm, SfFormItem, SfInput, SfButton },
    setup() {
      const form = reactive({ title: '', desc: '', tag: '' })
      function onSubmit() {
        alert(JSON.stringify(form))
      }
      return { form, onSubmit }
    },
    template: `
      <div style="max-width: 480px;">
        <SfForm @submit="onSubmit">
          <SfFormItem label="标题" required>
            <SfInput v-model="form.title" placeholder="取个好名字" />
          </SfFormItem>
          <SfFormItem label="标签">
            <SfInput v-model="form.tag" placeholder="选填" />
          </SfFormItem>
          <SfFormItem label="描述">
            <SfInput v-model="form.desc" :textarea="true" :rows="4" placeholder="补充说明..." />
          </SfFormItem>
          <SfButton type="primary" html-type="submit" block>发布</SfButton>
        </SfForm>
      </div>
    `
  })
}