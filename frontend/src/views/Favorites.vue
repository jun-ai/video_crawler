<template>
  <div class="yt-favorites">
    <SfEmpty v-if="!userStore.isLoggedIn" description="请先登录查看收藏">
      <SfButton type="primary" @click="$router.push('/login')">去登录</SfButton>
    </SfEmpty>

    <template v-else>
      <!-- 页面头部 -->
      <div class="fav-page-header">
        <SfButton type="ghost" size="sm" class="fav-back-btn" @click="$router.back()">
          <ArrowLeft :size="18" />
        </SfButton>
        <h1 class="fav-page-title">我的收藏</h1>
      </div>

      <!-- Tab 导航 - 绿色下划线风格 -->
      <div class="fav-tabs-row">
        <div class="fav-tabs">
          <div
            :class="['fav-tab', { active: activeTab === 'subtitles' }]"
            @click="activeTab = 'subtitles'"
          >
            <span>字幕</span>
            <span class="tab-count" v-if="subtitleTotal">{{ subtitleTotal }}</span>
          </div>
          <!-- 5-P1-1: 视频收藏 Tab (Phase 3 H5 移动端隐藏, H5 只要字幕 + 单词短语 2 tab) -->
          <div
            :class="['fav-tab', { 'fav-tab--desktop': true, active: activeTab === 'videos' }]"
            @click="activeTab = 'videos'"
          >
            <span>视频</span>
            <span class="tab-count" v-if="videoTotal">{{ videoTotal }}</span>
          </div>
          <div
            :class="['fav-tab', { active: activeTab === 'vocabulary' }]"
            @click="activeTab = 'vocabulary'"
          >
            <span>单词/短语</span>
            <span class="tab-count" v-if="vocabTotal">{{ vocabTotal }}</span>
          </div>
        </div>
        <!-- P2-5: 刷新按钮移到 Tab 行右侧 -->
        <SfButton type="ghost" size="sm" class="fav-refresh-btn" @click="refreshData" :loading="refreshing">
          <RefreshCw :size="14" />
        </SfButton>
      </div>

      <!-- 4-P1-5: 批量操作工具栏 (选中 N 项时出现) -->
      <Transition name="fav-bar">
        <div v-if="selectedIds.size > 0" class="fav-batch-bar">
          <span class="fav-batch-count">已选 {{ selectedIds.size }} 项</span>
          <SfButton size="sm" type="ghost" @click="clearSelection">
            <X :size="14" />
            取消
          </SfButton>
          <!-- 5-P2 (后缀): 多选删除 - 全选/反选当前筛选 -->
          <SfButton size="sm" type="ghost" @click="selectAllCurrent" :title="`全选当前 ${visibleBookmarkIds.length} 项`">
            <CheckCheck :size="14" />
            全选
          </SfButton>
          <SfButton size="sm" type="ghost" @click="invertSelection" :title="`反选当前 ${visibleBookmarkIds.length} 项`">
            <ArrowLeftRight :size="14" />
            反选
          </SfButton>
          <!-- 5-P1-2 (后缀): 批量移动到文件夹 -->
          <SfDropdown v-if="allFolders.length > 0">
            <template #trigger>
              <SfButton size="sm" type="ghost">
                <Move :size="14" />
                移动到
              </SfButton>
            </template>
            <div class="folder-picker-menu">
              <div
                v-for="f in allFolders"
                :key="f.id"
                class="dropdown-item"
                @click="batchMoveToFolder(f.id, f.name)"
              >
                <span class="folder-dot" :style="{ background: f.color || '#5c6ef5' }"></span>
                {{ f.name }}
                <span class="folder-pick-count">{{ f.bookmark_count }}</span>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item" @click="batchMoveToFolder(null, '未分类')">
                <FolderMinus :size="14" />
                未分类
              </div>
            </div>
          </SfDropdown>
          <SfButton size="sm" type="danger" @click="batchDelete">
            <Trash2 :size="14" />
            删除
          </SfButton>
        </div>
      </Transition>

      <!-- 4-P1-4: 字幕 Tab 搜索 + 视频筛选 -->
      <div v-if="activeTab === 'subtitles'" class="fav-filter-bar">
        <!-- 5-P1-2 (后缀): 文件夹 chip 行 (横向滚动, 默认显示全部/未分类) -->
        <div class="fav-folder-chips">
          <button
            :class="['fav-folder-chip', { active: filterFolderId === null }]"
            @click="filterFolderById(null)"
            aria-label="显示全部"
          >
            <Inbox :size="13" />
            <span>全部</span>
            <span class="fav-folder-count">{{ subtitleBookmarks.length }}</span>
          </button>
          <button
            :class="['fav-folder-chip', { active: filterFolderId === 0 }]"
            @click="filterFolderById(0)"
            aria-label="仅显示未分类"
            v-if="uncategorizedCount > 0"
          >
            <FolderMinus :size="13" />
            <span>未分类</span>
            <span class="fav-folder-count">{{ uncategorizedCount }}</span>
          </button>
          <button
            v-for="f in allFolders"
            :key="f.id"
            :class="['fav-folder-chip', { active: filterFolderId === f.id }]"
            :style="{ '--folder-color': f.color || '#5c6ef5' }"
            @click="filterFolderById(f.id)"
            :aria-label="`筛选文件夹 ${f.name}`"
          >
            <Folder :size="13" />
            <span>{{ f.name }}</span>
            <span class="fav-folder-count">{{ f.bookmark_count }}</span>
          </button>
          <button class="fav-folder-chip fav-folder-add" @click="openCreateFolder" aria-label="新建文件夹">
            <FolderPlus :size="13" />
            <span>新建</span>
          </button>
          <button v-if="allFolders.length > 0" class="fav-folder-chip fav-folder-manage" @click="showManageFolders = true" aria-label="管理文件夹">
            <Settings2 :size="13" />
            <span>管理</span>
          </button>
        </div>
        <!-- 5-P2 (后缀): 标签 chip 行 (5-P1-2 tags 筛选, 跟文件夹独立可组合) -->
        <div v-if="allUserTags.length > 0" class="fav-folder-chips fav-tag-chips">
          <button
            :class="['fav-folder-chip', 'fav-tag-chip', { active: filterTagId === null }]"
            @click="filterTagById(null)"
            aria-label="清除标签筛选"
          >
            <X :size="12" />
            <span>全部标签</span>
          </button>
          <button
            :class="['fav-folder-chip', 'fav-tag-chip', { active: filterTagId === 0 }]"
            @click="filterTagById(0)"
            aria-label="仅显示无标签"
          >
            <X :size="12" />
            <span>无标签</span>
          </button>
          <button
            v-for="t in allUserTags"
            :key="`tag-${t.id}`"
            :class="['fav-folder-chip', 'fav-tag-chip', { active: filterTagId === t.id }]"
            :style="{ '--folder-color': t.color || '#5c6ef5' }"
            @click="filterTagById(t.id)"
            :aria-label="`筛选标签 ${t.name}`"
          >
            <span class="user-tag-name">{{ t.name }}</span>
            <span class="fav-folder-count">{{ t.usage_count }}</span>
          </button>
        </div>
        <div class="fav-search-row">
          <div class="fav-search-wrap">
            <Search :size="14" class="fav-search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              class="fav-search-input"
              placeholder="搜索字幕 (英文/中文)..."
              aria-label="搜索字幕"
              @input="onSearchInput"
            />
            <button v-if="searchQuery" class="fav-search-clear" @click="clearSearch" aria-label="清空搜索">
              <X :size="14" />
            </button>
          </div>
          <div class="fav-material-filter">
            <!-- 5-P2-3: 语料 Combobox (可搜索, 替代下拉) -->
            <SfCombobox
              v-model="filterMaterialId"
              :options="availableMaterials.map(m => ({ value: m.id, label: m.title }))"
              placeholder="全部视频 (可搜索)"
              :display-value="filterMaterialTitle"
              class="filter-combobox"
            />
          </div>
          <!-- 5-P2 (后缀): 导出当前筛选 -->
          <SfDropdown>
            <template #trigger>
              <SfButton type="ghost" size="sm" :disabled="exporting" :loading="exporting">
                <Download :size="14" />
                导出
              </SfButton>
            </template>
            <div class="dropdown-menu">
              <div class="dropdown-item" @click="exportBookmarks('csv')">
                <span>CSV (Anki/Excel)</span>
              </div>
              <div class="dropdown-item" @click="exportBookmarks('json')">
                <span>JSON (完整备份)</span>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item fav-export-hint">
                <span class="fav-export-hint-text">
                  当前筛选: {{ exportFilterSummary }}
                </span>
              </div>
            </div>
          </SfDropdown>
        </div>
      </div>

      <!-- 字幕收藏 Tab -->
      <div v-show="activeTab === 'subtitles'" class="tab-content">
        <div class="subtitle-fav-list">
          <!-- P2-2: 骨架屏 -->
          <template v-if="subtitleLoading">
            <div v-for="i in 4" :key="`sk-${i}`" class="skeleton-fav-card">
              <div class="sk-line sk-title"></div>
              <div class="sk-line sk-sub"></div>
              <div class="sk-line sk-meta"></div>
            </div>
          </template>
          <div v-for="group in groupedSubtitles" :key="group.label" class="date-group">
            <div class="date-label">{{ group.label }}</div>
            <div class="subtitle-cards">
              <div
                v-for="item in group.items"
                :key="item.id"
                class="subtitle-fav-card"
                :class="{ selected: selectedIds.has(item.id) }"
              >
                <!-- 4-P1-5: 多选 checkbox -->
                <label class="fav-checkbox">
                  <input
                    type="checkbox"
                    :checked="selectedIds.has(item.id)"
                    @change="toggleSelect(item.id)"
                    :aria-label="`选择 ${item.text_en}`"
                  />
                </label>
                <!-- P2-3: 视频封面缩略图 (懒加载) -->
                <div class="fav-card-thumb" v-if="item.material_cover" @click="goMaterial(item.material_id)">
                  <img :src="item.material_cover" :alt="item.material_title || ''" loading="lazy" />
                </div>
                <div class="fav-card-content">
                  <div class="fav-card-english">{{ item.text_en }}</div>
                  <div class="fav-card-chinese" v-if="item.text_cn">"{{ item.text_cn }}"</div>

                  <!-- 5-P1-2: 笔记展示 (有 note 时) -->
                  <div v-if="item.note && !isEditingNote(item.id)" class="fav-card-note">
                    <StickyNote :size="13" class="note-icon" />
                    <span class="note-text">{{ item.note }}</span>
                    <button class="note-edit-btn" @click="startEditNote(item)" aria-label="编辑笔记">
                      <Edit2 :size="12" />
                    </button>
                  </div>

                  <!-- 5-P1-2: 笔记编辑 (textarea) -->
                  <div v-else-if="isEditingNote(item.id)" class="fav-card-note-edit">
                    <textarea
                      v-model="editingNote"
                      class="note-textarea"
                      placeholder="记点什么…(比如:这句很扎心, 收藏)"
                      maxlength="500"
                      rows="3"
                    ></textarea>
                    <div class="note-edit-actions">
                      <SfButton size="sm" type="ghost" @click="cancelEditNote">取消</SfButton>
                      <SfButton size="sm" type="primary" :disabled="savingNote" @click="saveEditNote(item)">
                        {{ savingNote ? '保存中…' : '保存' }}
                      </SfButton>
                    </div>
                  </div>

                  <!-- 5-P1-2: 添加笔记按钮 (无 note 且未编辑) -->
                  <div v-else class="fav-card-note-add">
                    <SfButton type="ghost" size="sm" @click="startEditNote(item)">
                      <Plus :size="13" /> 添加笔记
                    </SfButton>
                  </div>

                  <!-- 5-P1-2: 用户标签 chips (可点击移除) + 添加按钮 -->
                  <div class="fav-card-tags">
                    <TransitionGroup name="tag-chip">
                      <span
                        v-for="tag in (item.tags || [])"
                        :key="tag.id"
                        class="user-tag-chip"
                        :style="{ '--tag-color': tag.color || '#5c6ef5' }"
                      >
                        <span class="user-tag-name">{{ tag.name }}</span>
                        <button
                          class="user-tag-remove"
                          @click="removeTagFromBookmark(item, tag.name)"
                          :aria-label="`移除标签 ${tag.name}`"
                        >×</button>
                      </span>
                    </TransitionGroup>
                    <button
                      v-if="!isAddingTag(item.id)"
                      class="add-tag-btn"
                      @click="startAddTag(item)"
                      aria-label="添加标签"
                    >+ 标签</button>
                    <div v-else class="add-tag-input-wrap">
                      <input
                        :ref="el => tagInputRefs[item.id] = el"
                        v-model="tagInputValue"
                        class="add-tag-input"
                        :list="`tag-suggestions-${item.id}`"
                        placeholder="标签名, 回车确认"
                        maxlength="50"
                        @keydown.enter="confirmAddTag(item)"
                        @keydown.esc="cancelAddTag"
                        @keydown="onTagInputKeydown($event, item)"
                      />
                      <datalist :id="`tag-suggestions-${item.id}`">
                        <option v-for="t in allUserTags" :key="t.id" :value="t.name" />
                      </datalist>
                    </div>
                  </div>

                  <div class="fav-card-meta">
                    <!-- 5-P1-2 (后缀): 文件夹徽章 (有 folder 时显示) -->
                    <span
                      v-if="item.folder_name"
                      class="fav-card-folder"
                      :style="{ '--folder-color': item.folder_color || '#5c6ef5' }"
                      :title="`在文件夹 ${item.folder_name}`"
                    >
                      <Folder :size="12" />
                      {{ item.folder_name }}
                    </span>
                    <span class="fav-card-category">
                      <SfTag size="sm" type="default">{{ item.material_title || '未分类' }}</SfTag>
                    </span>
                    <span class="fav-card-duration">
                      {{ item.start_time ? formatDuration(item.start_time) : '' }}
                    </span>
                    <span v-if="item.practice_count > 0" class="fav-practice-count" :title="'已练习 ' + item.practice_count + ' 次'">
                      练习 {{ item.practice_count }} 次{{ formatLastPracticed(item.last_practiced_at) }}
                    </span>
                    <!-- P2-6: 移动端隐藏"未练习"灰色标签 (避免拥挤) -->
                    <span v-else class="fav-practice-count fav-practice-zero fav-practice-zero-mobile-hidden">未练习</span>
                  </div>
                </div>
                <div class="fav-card-actions">
                  <SfDropdown>
                    <template #trigger>
                      <MoreHorizontal :size="16" class="fav-more-icon" />
                    </template>
                    <!-- P2-1: 复制原句 -->
                    <div class="dropdown-item" @click="copySubtitleText(item)">
                      <Copy :size="14" />
                      复制原句
                    </div>
                    <!-- 5-P1-2 (后缀): 移动到文件夹 -->
                    <div v-if="allFolders.length > 0" class="dropdown-item fav-move-to-folder" @click.stop="openMoveToFolder(item)">
                      <Folder :size="14" />
                      {{ item.folder_name ? '换文件夹' : '移到文件夹' }}
                    </div>
                    <div v-if="item.folder_name" class="dropdown-item" @click="moveBookmarkToFolder(item, null)">
                      <FolderMinus :size="14" />
                      移出文件夹
                    </div>
                    <div class="dropdown-item" @click="handleSubtitleCommand('remove', item)">
                      <Trash2 :size="14" />
                      取消收藏
                    </div>
                  </SfDropdown>
                  <SfButton
                    type="ghost"
                    size="sm"
                    @click="quickPractice(item)"
                    class="fav-quick-practice-btn"
                    :title="'练习 (当前 ' + (item.practice_count || 0) + ' 次)'"
                  >
                    <RotateCcw :size="14" />
                  </SfButton>
                  <SfButton
                    type="primary"
                    size="sm"
                    @click="goLearnSubtitle(item)"
                    class="fav-practice-btn"
                  >
                    去练习
                    <ArrowRight :size="14" class="practice-arrow" />
                  </SfButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        <EmptyState
          v-if="!subtitleLoading && subtitleBookmarks.length === 0"
          type="no-favorites"
          title="还没有收藏字幕"
          description="在学习过程中，点击字幕旁的星标图标收藏感兴趣的句子"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去学习</SfButton>
          </template>
        </EmptyState>

        <div class="pagination" v-if="subtitleTotal > subtitlePageSize">
          <SfPagination
            :current-page="subtitlePage"
            :page-size="subtitlePageSize"
            :total="subtitleTotal"
            @change="loadSubtitleBookmarks"
          />
        </div>
      </div>

      <!-- 词汇收藏 Tab -->
      <div v-show="activeTab === 'vocabulary'" class="tab-content">
        <div class="vocab-list">
          <!-- P2-2: 骨架屏 -->
          <template v-if="vocabLoading">
            <div v-for="i in 4" :key="`vsk-${i}`" class="skeleton-fav-card">
              <div class="sk-line sk-title"></div>
              <div class="sk-line sk-sub"></div>
              <div class="sk-line sk-meta"></div>
            </div>
          </template>
          <div v-for="item in vocabList" :key="item.id" class="vocab-card">
            <div class="vocab-main">
              <div class="vocab-content">
                <div class="vocab-word-row">
                  <span class="vocab-word">{{ item.word }}</span>
                  <span class="vocab-phonetic" v-if="item.phonetic">/{{ item.phonetic }}/</span>
                  <SfButton
                    class="vocab-speak-btn"
                    size="sm"
                    @click="speakWord(item.word)"
                  >
                    <Headphones :size="14" />
                  </SfButton>
                </div>
                <div class="vocab-translation" v-if="item.translation">{{ item.translation }}</div>
                <div class="vocab-context" v-if="item.context">
                  <span class="context-label">来源：</span>{{ item.context }}
                </div>
              </div>
              <div class="vocab-actions">
                <SfDropdown>
                  <template #trigger>
                    <MoreHorizontal :size="16" class="fav-more-icon" />
                  </template>
                  <div class="dropdown-item" @click="handleVocabCommand('remove', item.id)">
                    <Trash2 :size="14" />
                    删除
                  </div>
                </SfDropdown>
                <!-- Phase 3 (H5): 对标规范 "去练习" 按钮 -->
                <SfButton
                  type="primary"
                  size="sm"
                  class="vocab-practice-btn"
                  @click="goPracticeVocab(item)"
                >
                  去练习
                </SfButton>
              </div>
            </div>
          </div>
        </div>

        <EmptyState
          v-if="!vocabLoading && vocabList.length === 0"
          type="no-vocabulary"
          title="生词本是空的"
          description="在学习过程中遇到的新单词可以添加到生词本"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去学习</SfButton>
          </template>
        </EmptyState>

        <div class="pagination" v-if="vocabTotal > vocabPageSize">
          <SfPagination
            :current-page="vocabPage"
            :page-size="vocabPageSize"
            :total="vocabTotal"
            @change="loadVocabList"
          />
        </div>
      </div>

      <!-- 5-P1-1: 视频收藏 Tab -->
      <div v-show="activeTab === 'videos'" class="tab-content fav-videos-tab">
        <div v-if="videoLoading" class="video-skeleton-list">
          <div v-for="i in 3" :key="i" class="video-skeleton-card"></div>
        </div>
        <div v-else-if="videoFavorites.length > 0" class="video-fav-grid">
          <div
            v-for="video in videoFavorites"
            :key="video.id"
            class="video-fav-card"
            @click="goMaterial(video.id)"
          >
            <div class="video-cover">
              <img
                v-if="video.cover_path"
                :src="video.cover_path"
                :alt="video.title"
                loading="lazy"
              />
              <div v-else class="video-cover-placeholder">
                <Film :size="32" />
              </div>
              <div v-if="video.duration" class="video-duration">
                {{ formatVideoDuration(video.duration) }}
              </div>
            </div>
            <div class="video-info">
              <div class="video-title" :title="video.title">{{ video.title }}</div>
              <div class="video-meta">
                <span v-if="video.difficulty">难度 {{ video.difficulty }}</span>
                <span v-if="video.favorited_at" class="video-fav-time">
                  <Heart :size="12" />
                  {{ formatRelativeTime(video.favorited_at) }}收藏
                </span>
              </div>
            </div>
            <button
              class="video-remove-btn"
              @click.stop="removeVideoFav(video)"
              aria-label="取消收藏"
            >
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
        <EmptyState
          v-else
          title="还没有收藏视频"
          description="在视频详情页点星标即可收藏"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去看看</SfButton>
          </template>
        </EmptyState>
      </div>
    </template>

    <!-- 5-P1-2 (后缀): 新建文件夹 / 移动到文件夹 弹层 -->
    <Teleport to="body">
      <Transition name="fav-modal">
        <div v-if="showCreateFolderModal" class="fav-modal-mask" @click.self="closeCreateFolder">
          <div class="fav-modal" @click.stop>
            <div class="fav-modal-header">
              <FolderPlus :size="18" />
              <span>新建文件夹</span>
            </div>
            <div class="fav-modal-body">
              <label class="fav-modal-label">名称</label>
              <input
                v-model="newFolderName"
                ref="newFolderInput"
                class="fav-modal-input"
                placeholder="比如: 商务英语"
                maxlength="50"
                @keydown.enter="submitCreateFolder"
                @keydown.esc="closeCreateFolder"
              />
              <label class="fav-modal-label">颜色 (可选)</label>
              <div class="fav-color-picker">
                <button
                  v-for="c in folderColors"
                  :key="c"
                  :class="['fav-color-dot', { active: newFolderColor === c }]"
                  :style="{ background: c }"
                  @click="newFolderColor = c"
                  :aria-label="`选择颜色 ${c}`"
                ></button>
              </div>
              <div v-if="createFolderError" class="fav-modal-error">{{ createFolderError }}</div>
            </div>
            <div class="fav-modal-actions">
              <SfButton type="ghost" @click="closeCreateFolder">取消</SfButton>
              <SfButton type="primary" :disabled="!newFolderName.trim() || creatingFolder" @click="submitCreateFolder">
                {{ creatingFolder ? '创建中…' : '创建' }}
              </SfButton>
            </div>
          </div>
        </div>
      </Transition>

      <!-- 移动到文件夹 picker (per-card 用) -->
      <Transition name="fav-modal">
        <div v-if="showMoveFolderFor" class="fav-modal-mask" @click.self="closeMoveToFolder">
          <div class="fav-modal" @click.stop>
            <div class="fav-modal-header">
              <Move :size="18" />
              <span>移动到文件夹</span>
            </div>
            <div class="fav-modal-body">
              <div
                class="dropdown-item fav-move-row"
                v-for="f in allFolders"
                :key="`mv-${f.id}`"
                @click="moveBookmarkToFolder(showMoveFolderFor, f.id)"
              >
                <span class="folder-dot" :style="{ background: f.color || '#5c6ef5' }"></span>
                {{ f.name }}
                <Check v-if="showMoveFolderFor.folder_id === f.id" :size="14" class="fav-move-check" />
              </div>
              <div class="dropdown-divider"></div>
              <div
                class="dropdown-item fav-move-row"
                @click="moveBookmarkToFolder(showMoveFolderFor, null)"
              >
                <FolderMinus :size="14" />
                未分类
                <Check v-if="!showMoveFolderFor.folder_id" :size="14" class="fav-move-check" />
              </div>
            </div>
            <div class="fav-modal-actions">
              <SfButton type="ghost" @click="closeMoveToFolder">关闭</SfButton>
            </div>
          </div>
        </div>
      </Transition>

      <!-- 文件夹管理 (删除 / 重命名 / 5-P2 (后缀) 拖拽排序) -->
      <Transition name="fav-modal">
        <div v-if="showManageFolders" class="fav-modal-mask" @click.self="showManageFolders = false">
          <div class="fav-modal fav-modal-wide" @click.stop>
            <div class="fav-modal-header">
              <Folder :size="18" />
              <span>管理文件夹 ({{ allFolders.length }})</span>
              <span class="fav-manage-tip">拖拽或点 ↑↓ 排序</span>
            </div>
            <div class="fav-modal-body fav-manage-list">
              <div v-if="allFolders.length === 0" class="fav-manage-empty">
                还没有文件夹, 点下方"新建文件夹"创建第一个
              </div>
              <div
                v-for="(f, idx) in allFolders"
                :key="`mg-${f.id}`"
                class="fav-manage-row"
                :draggable="true"
                @dragstart="onFolderDragStart($event, idx)"
                @dragover.prevent="onFolderDragOver($event, idx)"
                @dragend="onFolderDragEnd"
                :class="{ 'fav-drag-over': dragOverIndex === idx }"
              >
                <GripVertical :size="14" class="fav-drag-handle" />
                <span class="folder-dot" :style="{ background: f.color || '#5c6ef5' }"></span>
                <span class="fav-manage-name">{{ f.name }}</span>
                <span class="fav-manage-count">{{ f.bookmark_count }} 项</span>
                <!-- 5-P2 (后缀): 上下移动按钮 -->
                <SfButton size="sm" type="ghost" @click="moveFolderOrder(f, -1)" :disabled="idx === 0" aria-label="上移">
                  <ChevronUp :size="13" />
                </SfButton>
                <SfButton size="sm" type="ghost" @click="moveFolderOrder(f, 1)" :disabled="idx === allFolders.length - 1" aria-label="下移">
                  <ChevronDown :size="13" />
                </SfButton>
                <SfButton size="sm" type="ghost" @click="openRenameFolderDialog(f)" aria-label="重命名">
                  <Edit2 :size="13" />
                </SfButton>
                <SfButton size="sm" type="danger" @click="deleteFolderConfirm(f)" aria-label="删除">
                  <Trash2 :size="13" />
                </SfButton>
              </div>
            </div>
            <div class="fav-modal-actions">
              <SfButton type="ghost" @click="showManageFolders = false">关闭</SfButton>
              <SfButton type="primary" @click="openCreateFolder">新建文件夹</SfButton>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- P2-6 (UI 统一): 重命名文件夹弹窗 (替代 window.prompt) -->
    <SfDialog
      v-model="renameDialog.open"
      :title="`重命名文件夹`"
      width="420px"
      @close="closeRenameFolderDialog"
    >
      <div class="fav-rename-body">
        <label class="fav-rename-label">新名称</label>
        <SfInput
          v-model="renameDialog.name"
          placeholder="输入新名称"
          :maxlength="30"
          @keydown.enter="submitRenameFolder"
        />
        <p class="fav-rename-hint">文件夹名 1-30 字符, 重名会提示冲突</p>
      </div>
      <template #footer>
        <SfButton type="ghost" @click="closeRenameFolderDialog">取消</SfButton>
        <SfButton
          type="primary"
          :loading="renamingFolder"
          :disabled="!renameDialog.name.trim() || renameDialog.name.trim() === renameDialog.folder?.name"
          @click="submitRenameFolder"
        >
          保存
        </SfButton>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import { showConfirm } from '@/composables/useConfirm'
import {
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  MoreHorizontal,
  Trash2,
  Headphones,
  // 4-P1-4: 搜索 + 视频筛选图标
  Search,
  X,
  Filter,
  // 5-P1-1: 视频收藏 Tab
  Film,
  Heart,
  // 5-P1-2: 笔记
  StickyNote,
  Edit2,
  Plus,
  // P2-1/P2-4: 复制原句 + 快速复习
  Copy,
  RotateCcw,
  // 5-P1-2 (后缀): 文件夹
  Folder,
  FolderPlus,
  FolderMinus,
  Inbox,
  Move,
  Check,
  Settings2,
  // 5-P2 (后缀): 多选删除增强 (全选/反选)
  CheckCheck,
  ArrowLeftRight,
  // 5-P2 (后缀): 文件夹拖拽排序
  GripVertical,
  ChevronUp,
  ChevronDown,
  // 5-P2 (后缀): 导出
  Download
} from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfCombobox from '@/components/ui/SfCombobox.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { favoriteAPI, vocabularyAPI, subtitleBookmarkAPI, materialAPI, bookmarkTagAPI, bookmarkFolderAPI, bookmarkExportAPI } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { speakWord, preloadVoices } = useTTS()

// Tab 控制
const activeTab = ref('subtitles')
const refreshing = ref(false)

// ====== 字幕收藏 ======
const subtitleLoading = ref(false)
const subtitleBookmarks = ref([])
// 分页由前端 slice（不依赖服务端分页，单次拉全部）
const subtitlePage = ref(1)
const subtitlePageSize = ref(20)
const subtitleTotal = ref(0)

// 按日期分组
const groupedSubtitles = computed(() => {
  // P2-8: 最近 7 天用语义化标签 (今天/昨天/N天前), 超过 7 天用真实日期 (MM-DD)
  const groups = {}
  const order = []
  subtitleBookmarks.value.forEach(item => {
    const date = item.created_at ? new Date(item.created_at) : new Date()
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    let label
    if (days === 0) label = '今天'
    else if (days === 1) label = '昨天'
    else if (days < 7) label = `${days} 天前`
    else {
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      label = `${date.getFullYear()}-${m}-${d}`
    }

    if (!groups[label]) {
      groups[label] = { label, items: [], _sortKey: date.getTime() }
      order.push(label)
    }
    groups[label].items.push(item)
  })

  // 按时间倒序 (最新的组在前)
  return Object.values(groups).sort((a, b) => b._sortKey - a._sortKey)
})

// ====== 词汇收藏 ======
const vocabLoading = ref(false)
const vocabList = ref([])
const vocabPage = ref(1)
const vocabPageSize = ref(20)
const vocabTotal = ref(0)

const formatDuration = (ms) => {
  if (!ms && ms !== 0) return ''
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${min}:${String(sec).padStart(2, '0')}`
}

// P2-4: 格式化"最后练习时间" (相对时间)
const formatLastPracticed = (isoStr) => {
  if (!isoStr) return ''
  const date = new Date(isoStr)
  const now = new Date()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)
  if (diffMin < 1) return ' · 刚刚'
  if (diffMin < 60) return ` · ${diffMin} 分钟前`
  if (diffHr < 24) return ` · ${diffHr} 小时前`
  if (diffDay < 30) return ` · ${diffDay} 天前`
  return ` · ${date.getMonth() + 1}/${date.getDate()}`
}

// P2-1: 复制原句到剪贴板
const copySubtitleText = async (item) => {
  const text = item.text_cn ? `${item.text_en}\n"${item.text_cn}"` : item.text_en
  try {
    await navigator.clipboard.writeText(text)
    toast.success('已复制')
  } catch {
    toast.error('复制失败')
  }
}

// P2-4: 快速复习 (increment practice_count)
const quickPractice = async (item) => {
  try {
    await subtitleBookmarkAPI.incrementPractice(item.id)
    item.practice_count = (item.practice_count || 0) + 1
    item.last_practiced_at = new Date().toISOString()
  } catch (e) {
    console.error('练习失败', e)
    toast.error('练习失败')
  }
}

// ====== 字幕收藏操作 ======

// 4-P1-4: 搜索 + 视频筛选
const searchQuery = ref('')
const filterMaterialId = ref(null)
let searchDebounce = null

// 5-P1-1: 视频收藏 (Favorite material 级别)
const videoFavorites = ref([])
const videoLoading = ref(false)
const videoTotal = ref(0)

const goMaterial = (id) => {
  router.push(`/materials/${id}`)
}

const removeVideoFav = async (video) => {
  const confirmed = await showConfirm({
    title: '取消收藏',
    message: `确定要取消收藏视频「${video.title}」吗？`
  })
  if (!confirmed) return
  try {
    await favoriteAPI.remove(video.id)
    toast.success('已取消收藏')
    await loadVideoFavorites()
  } catch (e) {
    console.error('取消收藏失败', e)
    toast.error('取消收藏失败')
  }
}

const formatVideoDuration = (seconds) => {
  if (!seconds || seconds < 0) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const loadVideoFavorites = async () => {
  if (!userStore.isLoggedIn) return
  videoLoading.value = true
  try {
    const res = await favoriteAPI.getList({ page: 1, page_size: 50 })
    videoFavorites.value = res.items || []
    videoTotal.value = res.total || 0
  } catch (e) {
    console.error('加载视频收藏失败', e)
    videoFavorites.value = []
    videoTotal.value = 0
  } finally {
    videoLoading.value = false
  }
}

// 5-P1-2: 笔记编辑
const editingNoteId = ref(null)
const editingNote = ref('')
const savingNote = ref(false)

const isEditingNote = (id) => editingNoteId.value === id

const startEditNote = (item) => {
  editingNoteId.value = item.id
  editingNote.value = item.note || ''
}

const cancelEditNote = () => {
  editingNoteId.value = null
  editingNote.value = ''
}

const saveEditNote = async (item) => {
  savingNote.value = true
  try {
    const res = await subtitleBookmarkAPI.update(item.id, { note: editingNote.value })
    item.note = res.note
    cancelEditNote()
    toast.success('笔记已保存')
  } catch (e) {
    console.error('保存笔记失败', e)
    toast.error('保存失败')
  } finally {
    savingNote.value = false
  }
}

// ==================== 5-P1-2: 用户标签 ====================
// 用户自有标签 (bookmark 维度), 与全局 Tag (material 维度) 区分
const allUserTags = ref([])            // 所有标签 (含 usage_count, 用于 datalist 补全)
const addingTagBookmarkId = ref(null)  // 正在添加标签的 bookmark id
const tagInputValue = ref('')
const tagInputRefs = ref({})           // 多个 input 的 ref 收集

// 加载所有用户标签 (onMounted + add/remove 后刷新)
const loadUserTags = async () => {
  try {
    const res = await bookmarkTagAPI.list()
    allUserTags.value = res || []
  } catch (e) {
    console.error('加载标签失败', e)
  }
}

const isAddingTag = (id) => addingTagBookmarkId.value === id

const startAddTag = (item) => {
  addingTagBookmarkId.value = item.id
  tagInputValue.value = ''
  // nextTick 聚焦
  setTimeout(() => {
    const el = tagInputRefs.value[item.id]
    if (el && typeof el.focus === 'function') el.focus()
  }, 50)
}

const cancelAddTag = () => {
  addingTagBookmarkId.value = null
  tagInputValue.value = ''
}

const confirmAddTag = async (item) => {
  const name = tagInputValue.value.trim()
  if (!name) {
    cancelAddTag()
    return
  }
  // 拼接现有 + 新的, 一次性 setTags (replace-all)
  const currentNames = (item.tags || []).map(t => t.name)
  if (currentNames.includes(name)) {
    toast.info('已有此标签')
    cancelAddTag()
    return
  }
  const newNames = [...currentNames, name]
  try {
    await subtitleBookmarkAPI.setTags(item.id, newNames)
    // 乐观更新 (无需重新拉 list)
    item.tags = [...(item.tags || []), { id: Date.now(), name, color: '#5c6ef5' }]
    await loadUserTags()  // 刷新 allUserTags (usage_count)
    cancelAddTag()
  } catch (e) {
    console.error('添加标签失败', e)
    toast.error('添加失败')
  }
}

const removeTagFromBookmark = async (item, tagName) => {
  const newNames = (item.tags || []).filter(t => t.name !== tagName).map(t => t.name)
  try {
    await subtitleBookmarkAPI.setTags(item.id, newNames)
    item.tags = (item.tags || []).filter(t => t.name !== tagName)
    await loadUserTags()
  } catch (e) {
    console.error('移除标签失败', e)
    toast.error('移除失败')
  }
}

// datalist 不支持键盘补全确认, 这个是预留扩展点 (目前用原生 datalist)
const onTagInputKeydown = (e, item) => {
  // 未来如需自定义补全 dropdown, 在这里处理 ArrowUp/Down/Enter
}

// 4-P1-5: 批量选择
const selectedIds = ref(new Set())

const toggleSelect = (id) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

// 5-P2 (后缀): 当前筛选可见的 bookmark id 列表 (用于全选/反选)
const visibleBookmarkIds = computed(() => {
  // subtitleBookmarks 已经按当前筛选 (folder/tag/search) 过滤了
  return subtitleBookmarks.value.map(b => b.id)
})

const selectAllCurrent = () => {
  // 合并当前可见 + 已选
  const next = new Set(selectedIds.value)
  for (const id of visibleBookmarkIds.value) {
    next.add(id)
  }
  selectedIds.value = next
}

const invertSelection = () => {
  // 可见项中, 已选 → 反选未选, 未选 → 选上
  const visible = new Set(visibleBookmarkIds.value)
  const next = new Set()
  for (const id of visible) {
    if (!selectedIds.value.has(id)) {
      next.add(id)
    }
  }
  // 已选但不可见 (筛选变了) 的保留
  for (const id of selectedIds.value) {
    if (!visible.has(id)) {
      next.add(id)
    }
  }
  selectedIds.value = next
}

// 4-P1-5: 批量删除 + Undo (5-P2 后缀增强: 真实撤销 + 显示文件夹信息)
const batchDelete = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return

  // 5-P2 (后缀): 统计涉及多少个文件夹 (让用户知道会丢失哪些组织)
  const itemsToDelete = subtitleBookmarks.value.filter(b => ids.includes(b.id))
  const folderNames = new Set()
  let untaggedCount = 0
  for (const item of itemsToDelete) {
    if (item.folder_name) folderNames.add(item.folder_name)
    else untaggedCount++
  }
  const folderHint = folderNames.size > 0
    ? ` (涉及 ${folderNames.size} 个文件夹${untaggedCount > 0 ? ` + ${untaggedCount} 项未分类` : ''})`
    : (untaggedCount > 0 ? ` (都是未分类)` : '')

  const confirmed = await showConfirm({
    title: '批量删除',
    message: `确定删除选中的 ${ids.length} 项字幕收藏？${folderHint}`
  })
  if (!confirmed) return

  // 备份被删的 items (用于真实撤销: 重新 add 回来)
  const backupItems = itemsToDelete.map(b => ({
    material_id: b.material_id,
    subtitle_id: b.subtitle_id,
    note: b.note,
    folder_id: b.folder_id
  }))
  try {
    const res = await subtitleBookmarkAPI.batchDelete(ids)
    const deletedCount = parseInt(res.message.match(/\d+/)?.[0] || ids.length)
    clearSelection()
    loadSubtitleBookmarks()
    toast.withAction(
      `已删除 ${deletedCount} 项`,
      {
        label: '撤销',
        onClick: async () => {
          // 5-P2 (后缀): 真实撤销 - 逐个 add 回来 (note/folder 保留)
          let restored = 0
          let failed = 0
          toast.info(`恢复中… 0/${backupItems.length}`)
          for (const item of backupItems) {
            try {
              await subtitleBookmarkAPI.add({
                material_id: item.material_id,
                subtitle_id: item.subtitle_id,
                note: item.note,
                folder_id: item.folder_id
              })
              restored++
            } catch (e) {
              // 重复收藏 (字幕已重新收藏) → 跳过
              failed++
            }
          }
          await loadSubtitleBookmarks()
          if (failed > 0) {
            toast.success(`已恢复 ${restored} 项, ${failed} 项跳过 (已存在)`)
          } else {
            toast.success(`已恢复 ${restored} 项`)
          }
        }
      },
      { type: 'success', duration: 6000 }
    )
  } catch (e) {
    console.error('批量删除失败', e)
    toast.error('批量删除失败')
  }
}

const availableMaterials = computed(() => {
  // 从已加载的 bookmarks 提取去重的视频列表
  const map = new Map()
  for (const item of subtitleBookmarks.value) {
    if (item.material_id && !map.has(item.material_id)) {
      map.set(item.material_id, { id: item.material_id, title: item.material_title })
    }
  }
  return Array.from(map.values()).sort((a, b) => a.title.localeCompare(b.title, 'zh'))
})

const filterMaterialTitle = computed(() => {
  if (!filterMaterialId.value) return null
  return availableMaterials.value.find(m => m.id === filterMaterialId.value)?.title || null
})

const onSearchInput = () => {
  // 防抖 300ms 避免连续输入狂触发
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadSubtitleBookmarks(), 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  loadSubtitleBookmarks()
}

const filterMaterialById = (id) => {
  filterMaterialId.value = id
  loadSubtitleBookmarks()
}

const loadSubtitleBookmarks = async () => {
  if (!userStore.isLoggedIn) return
  subtitleLoading.value = true
  try {
    // 4-P1-4: 传 search + material_id 参数
    // 5-P1-2 (后缀): 加 folder_id 过滤 (null=全部, 0=未分类, 其他=该 folder)
    const params = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterMaterialId.value) params.material_id = filterMaterialId.value
    if (filterFolderId.value !== null) params.folder_id = filterFolderId.value
    if (filterTagId.value !== null) params.tag_id = filterTagId.value
    const res = await subtitleBookmarkAPI.getAll(params)
    const items = Array.isArray(res) ? res : (res.items || [])
    // 字段映射：后端 subtitle_text_en → 前端 text_en
    subtitleBookmarks.value = items.map(item => ({
      id: item.id,
      subtitle_id: item.subtitle_id,
      material_id: item.material_id,
      material_title: item.material_title || '未分类',
      text_en: item.subtitle_text_en || '',
      text_cn: item.subtitle_text_cn || '',
      start_time: item.subtitle_start_time,
      practice_count: item.practice_count || 0,
      last_practiced_at: item.last_practiced_at,
      note: item.note,
      tags: item.tags || [],
      // 5-P1-2 (后缀): 文件夹信息
      folder_id: item.folder_id || null,
      folder_name: item.folder_name || null,
      folder_color: item.folder_color || null,
    }))
    subtitleTotal.value = items.length
  } catch (e) {
    console.error('加载字幕收藏失败', e)
  } finally {
    subtitleLoading.value = false
  }
}

const goLearnSubtitle = (item) => {
  if (item.material_id) {
    // 3.7 带时间戳跳转, 避免用户点收藏后还要手动找
    const startTime = item.start_time
    const query = startTime != null ? `?start_time=${encodeURIComponent(startTime)}` : ''
    router.push(`/learn/${item.material_id}${query}`)
  }
}

const handleSubtitleCommand = async (command, item) => {
  if (command === 'remove') {
    const confirmed = await showConfirm({ title: '提示', message: '确定要取消收藏吗？' })
    if (confirmed) {
      try {
        await subtitleBookmarkAPI.remove(item.id)
        toast.success('已取消收藏')
        loadSubtitleBookmarks()
      } catch (e) {
        console.error('取消收藏失败', e)
      }
    }
  }
}

// ====== 词汇操作 ======

const loadVocabList = async () => {
  if (!userStore.isLoggedIn) return
  vocabLoading.value = true
  try {
    const res = await vocabularyAPI.getList({
      page: vocabPage.value,
      page_size: vocabPageSize.value
    })
    vocabList.value = res.items || []
    vocabTotal.value = res.total || 0
  } catch (e) {
    console.error('加载词汇失败', e)
  } finally {
    vocabLoading.value = false
  }
}

// speakWord 由 useTTS 提供

// Phase 3 (H5): 对标规范"去练习"按钮 - 跳到生词复习页
const goPracticeVocab = (item) => {
  if (!item?.word) {
    toast.error('无法定位该词')
    return
  }
  // 跳到生词复习页, 携带 word 参数让复习页聚焦这个词
  router.push({ path: '/vocabulary-review', query: { word: item.word } })
}

const handleVocabCommand = async (command, vocabId) => {
  if (command === 'remove') {
    const confirmed = await showConfirm({ title: '提示', message: '确定要删除这个词汇吗？' })
    if (confirmed) {
      try {
        await vocabularyAPI.delete(vocabId)
        toast.success('已删除')
        loadVocabList()
      } catch (e) {
        console.error('删除词汇失败', e)
      }
    }
  }
}

// ====== 刷新 ======
const refreshData = async () => {
  refreshing.value = true
  try {
    await Promise.all([
    loadSubtitleBookmarks(),
    loadVocabList(),
    loadVideoFavorites(),  // 5-P1-1
    loadFolders()  // 5-P1-2 (后缀): 文件夹
  ])
  } finally {
    refreshing.value = false
  }
}

// ==================== 5-P1-2 (后缀): 收藏文件夹 ====================
// 状态
const allFolders = ref([])         // [{ id, name, color, icon, bookmark_count }]
const filterFolderId = ref(null)   // null=全部, 0=未分类, 其他=该 folder
const filterTagId = ref(null)      // 5-P2 (后缀): null=全部, 0=无标签, 其他=该 tag (跟 folder 可组合)
const uncategorizedCount = computed(() => {
  // 从当前已加载的 bookmarks 推断未分类数 (无 folder_id)
  return subtitleBookmarks.value.filter(b => !b.folder_id).length
})

// 颜色选择器 (7 种主色, 跟用户标签配色一致)
const folderColors = [
  '#5c6ef5', '#ef4444', '#f59e0b', '#22c55e',
  '#06b6d4', '#a855f7', '#ec4899'
]

// 加载所有文件夹
const loadFolders = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await bookmarkFolderAPI.list()
    allFolders.value = res || []
  } catch (e) {
    console.error('加载文件夹失败', e)
    allFolders.value = []
  }
}

// 按文件夹筛选
const filterFolderById = (id) => {
  filterFolderId.value = id
  loadSubtitleBookmarks()
}

// 5-P2 (后缀): 按标签筛选
const filterTagById = (id) => {
  filterTagId.value = id
  loadSubtitleBookmarks()
}

// ====== 新建文件夹弹层 ======
const showCreateFolderModal = ref(false)
const newFolderName = ref('')
const newFolderColor = ref('#5c6ef5')
const creatingFolder = ref(false)
const createFolderError = ref('')
const newFolderInput = ref(null)

const openCreateFolder = () => {
  showCreateFolderModal.value = true
  newFolderName.value = ''
  newFolderColor.value = '#5c6ef5'
  createFolderError.value = ''
  // nextTick 聚焦
  setTimeout(() => {
    if (newFolderInput.value && newFolderInput.value.focus) {
      newFolderInput.value.focus()
    }
  }, 100)
  // 关闭管理面板 (避免堆叠)
  showManageFolders.value = false
}

const closeCreateFolder = () => {
  showCreateFolderModal.value = false
  newFolderName.value = ''
  createFolderError.value = ''
}

const submitCreateFolder = async () => {
  const name = newFolderName.value.trim()
  if (!name) return
  creatingFolder.value = true
  createFolderError.value = ''
  try {
    const res = await bookmarkFolderAPI.create({ name, color: newFolderColor.value })
    allFolders.value = [res, ...allFolders.value]
    toast.success(`已创建文件夹 "${res.name}"`)
    closeCreateFolder()
  } catch (e) {
    // 409 重名
    if (e?.response?.status === 409) {
      createFolderError.value = e.response.data?.detail || '文件夹名已存在'
    } else {
      createFolderError.value = e?.response?.data?.detail || '创建失败'
    }
  } finally {
    creatingFolder.value = false
  }
}

// ====== 移动单个 bookmark 到文件夹 ======
const showMoveFolderFor = ref(null)  // 当前正在操作的 bookmark 对象

const openMoveToFolder = (item) => {
  showMoveFolderFor.value = item
}

const closeMoveToFolder = () => {
  showMoveFolderFor.value = null
}

const moveBookmarkToFolder = async (item, folderId) => {
  try {
    await bookmarkFolderAPI.moveBookmark(item.id, folderId)
    // 乐观更新本地
    const folder = folderId ? allFolders.value.find(f => f.id === folderId) : null
    item.folder_id = folderId
    item.folder_name = folder?.name || null
    item.folder_color = folder?.color || null
    // 刷新 bookmark_count
    await loadFolders()
    toast.success(folderId ? `已移到 "${folder?.name}"` : '已移出文件夹')
    closeMoveToFolder()
  } catch (e) {
    console.error('移动失败', e)
    toast.error('移动失败')
  }
}

// ====== 批量移动 ======
const batchMoveToFolder = async (folderId, folderName) => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  try {
    const res = await bookmarkFolderAPI.batchMove(ids, folderId)
    // 乐观更新本地
    for (const id of ids) {
      const bm = subtitleBookmarks.value.find(b => b.id === id)
      if (bm) {
        const folder = folderId ? allFolders.value.find(f => f.id === folderId) : null
        bm.folder_id = folderId
        bm.folder_name = folder?.name || null
        bm.folder_color = folder?.color || null
      }
    }
    await loadFolders()
    toast.success(res.message || '已移动')
    // 移动后清空选择
    clearSelection()
  } catch (e) {
    console.error('批量移动失败', e)
    toast.error('批量移动失败')
  }
}

// ====== 文件夹管理 (重命名 / 删除) ======
const showManageFolders = ref(false)

// P2-6 (UI 统一): 改用 SfDialog 弹窗替代 window.prompt
const renameDialog = ref({ open: false, folder: null, name: '' })
const renamingFolder = ref(false)

const openRenameFolderDialog = (f) => {
  renameDialog.value = { open: true, folder: f, name: f.name }
}
const closeRenameFolderDialog = () => {
  renameDialog.value.open = false
}

const submitRenameFolder = async () => {
  const f = renameDialog.value.folder
  const newName = renameDialog.value.name.trim()
  if (!f || !newName || newName === f.name) {
    closeRenameFolderDialog()
    return
  }
  renamingFolder.value = true
  try {
    await bookmarkFolderAPI.update(f.id, { name: newName })
    f.name = newName
    // 同步更新已显示的 bookmark 上的 folder_name
    for (const bm of subtitleBookmarks.value) {
      if (bm.folder_id === f.id) bm.folder_name = f.name
    }
    toast.success('已重命名')
    closeRenameFolderDialog()
  } catch (e) {
    if (e?.response?.status === 409) {
      toast.error(e.response.data?.detail || '重名')
    } else {
      toast.error('重命名失败')
    }
  } finally {
    renamingFolder.value = false
  }
}

const deleteFolderConfirm = async (f) => {
  const confirmed = await showConfirm({
    title: '删除文件夹',
    message: `确定删除文件夹 "${f.name}"? 里面的 ${f.bookmark_count} 项收藏会变"未分类".`
  })
  if (!confirmed) return
  try {
    await bookmarkFolderAPI.delete(f.id)
    // 从本地移除
    allFolders.value = allFolders.value.filter(x => x.id !== f.id)
    // 同步: 该 folder 下的 bookmark.folder_id = null
    for (const bm of subtitleBookmarks.value) {
      if (bm.folder_id === f.id) {
        bm.folder_id = null
        bm.folder_name = null
        bm.folder_color = null
      }
    }
    // 如果当前正在筛选该 folder, 切回"全部"
    if (filterFolderId.value === f.id) {
      filterFolderId.value = null
      loadSubtitleBookmarks()
    }
    toast.success(`已删除 "${f.name}"`)
  } catch (e) {
    console.error('删除失败', e)
    toast.error('删除失败')
  }
}

// ==================== 5-P2 (后缀): 文件夹拖拽排序 ====================
// 用原生 HTML5 拖拽 + 上下按钮 (双方案)
// 后端 bookmark_folders.sort_order 越大越靠前, 列表 desc 排序
// 策略: 移动后给所有 folder 重新分配连续的 sort_order (gap 100, 留扩展空间)
const dragFromIndex = ref(null)
const dragOverIndex = ref(null)

const onFolderDragStart = (e, idx) => {
  dragFromIndex.value = idx
  // 设置拖拽数据 (required for Firefox)
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', String(idx))
}

const onFolderDragOver = (e, idx) => {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
  dragOverIndex.value = idx
}

const onFolderDragEnd = async () => {
  const from = dragFromIndex.value
  const to = dragOverIndex.value
  dragFromIndex.value = null
  dragOverIndex.value = null
  if (from === null || to === null || from === to) return
  // 重新排序 allFolders
  const next = [...allFolders.value]
  const [moved] = next.splice(from, 1)
  next.splice(to, 0, moved)
  allFolders.value = next
  await persistFolderOrder(next)
}

// 上下按钮: direction -1=上移, 1=下移
const moveFolderOrder = async (f, direction) => {
  const idx = allFolders.value.findIndex(x => x.id === f.id)
  if (idx === -1) return
  const newIdx = idx + direction
  if (newIdx < 0 || newIdx >= allFolders.value.length) return
  const next = [...allFolders.value]
  const [moved] = next.splice(idx, 1)
  next.splice(newIdx, 0, moved)
  allFolders.value = next
  await persistFolderOrder(next)
}

// 持久化: 给每个 folder 分配 sort_order (gap 100, desc → 越后越大)
const persistFolderOrder = async (orderedList) => {
  try {
    // 逐个 PATCH sort_order (N 个请求, 但 folder 数量小 ≤ 30)
    const total = orderedList.length
    for (let i = 0; i < total; i++) {
      const f = orderedList[i]
      const newOrder = (total - i) * 100  // 第一项最大
      await bookmarkFolderAPI.update(f.id, { sort_order: newOrder })
    }
    // 刷新确保后端顺序一致
    await loadFolders()
  } catch (e) {
    console.error('保存排序失败', e)
    toast.error('保存排序失败')
    // 回滚
    await loadFolders()
  }
}

// ==================== 5-P2 (后缀): 导出当前筛选 ====================
// 复用所有筛选条件 (search/material_id/folder_id/tag_id) 导成 csv/json
// 浏览器自动下载, 文件名后端带时间戳
const exporting = ref(false)

const exportFilterSummary = computed(() => {
  const parts = []
  if (searchQuery.value.trim()) parts.push(`搜索"${searchQuery.value.trim()}"`)
  if (filterMaterialId.value) {
    const m = availableMaterials.value.find(x => x.id === filterMaterialId.value)
    if (m) parts.push(`视频"${m.title}"`)
  }
  if (filterFolderId.value !== null) {
    if (filterFolderId.value === 0) parts.push('未分类')
    else {
      const f = allFolders.value.find(x => x.id === filterFolderId.value)
      parts.push(f ? `文件夹"${f.name}"` : '该文件夹')
    }
  }
  if (filterTagId.value !== null) {
    if (filterTagId.value === 0) parts.push('无标签')
    else {
      const t = allUserTags.value.find(x => x.id === filterTagId.value)
      parts.push(t ? `标签"${t.name}"` : '该标签')
    }
  }
  if (parts.length === 0) return '全部 (无筛选)'
  return `${parts.join(' + ')} (${subtitleBookmarks.value.length} 项)`
})

const exportBookmarks = async (format) => {
  if (exporting.value) return
  exporting.value = true
  try {
    const params = { format }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterMaterialId.value) params.material_id = filterMaterialId.value
    if (filterFolderId.value !== null) params.folder_id = filterFolderId.value
    if (filterTagId.value !== null) params.tag_id = filterTagId.value

    const res = await bookmarkExportAPI.download(params)
    // 从 Content-Disposition 拿文件名 (回退用)
    const cd = res.headers['content-disposition'] || ''
    const match = cd.match(/filename=([^;]+)/)
    const filename = match ? match[1] : `bookmarks.${format}`

    // 创建 Blob URL 触发下载
    const blob = new Blob([res.data], {
      type: format === 'json' ? 'application/json' : 'text/csv;charset=utf-8'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success(`已导出 ${subtitleBookmarks.value.length} 项`)
  } catch (e) {
    console.error('导出失败', e)
    toast.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  preloadVoices()
  if (userStore.isLoggedIn) {
    loadSubtitleBookmarks()
    loadVocabList()
    loadUserTags()
    loadFolders()
  }
})
</script>

<style scoped>
/* ================================================
   Favorites — Phase 2 CSS-only redesign
   Design system: ink green #2563EB + warm orange #F59E0B
   ================================================ */

.yt-favorites {
  max-width: 900px;
  margin: 0 auto;
}

/* ====== Page header ====== */
.fav-page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0 24px;
  position: relative;
}

.fav-back-btn {
  color: var(--color-text-primary);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-back-btn:hover {
  background: var(--color-brand-subtle);
  border-color: var(--color-brand-bright);
  color: var(--color-brand-bright);
}

.fav-page-title {
  flex: 1;
  font-size: var(--text-2xl, 24px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.fav-manage-btn {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  border-color: var(--color-border);
  background: var(--color-bg-card);
  min-height: 44px;
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-manage-btn:hover {
  color: var(--color-brand-bright);
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

/* ====== Tab navigation — underline style ====== */
.fav-tabs {
  display: flex;
  gap: 32px;
  padding: 0 4px;
  margin-bottom: 28px;
  border-bottom: 2px solid var(--color-border);
}

.fav-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 4px;
  font-size: var(--text-base, 16px);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: color var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  min-height: 44px;
}

.fav-tab:hover {
  color: var(--color-text-primary);
}

.fav-tab.active {
  color: var(--color-brand-bright);
  font-weight: 600;
}

.fav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--sf-brand-gradient);
  border-radius: 3px 3px 0 0;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 20px;
  padding: 0 6px;
  font-size: var(--text-xs, 11px);
  font-weight: 600;
  border-radius: 10px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.fav-tab.active .tab-count {
  background: var(--color-brand-subtle);
  color: var(--color-brand-bright);
}

.tab-content {
  min-height: 200px;
}

/* ====== Subtitle favorites list ====== */
.subtitle-fav-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.date-label {
  font-size: var(--text-xs, 12px);
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 14px;
  padding-left: 2px;
}

.subtitle-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subtitle-fav-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  padding: 20px;
  gap: 16px;
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  position: relative;
}

.subtitle-fav-card.selected {
  background: rgba(37, 99, 235, 0.04);
  outline: 2px solid var(--color-brand);
  outline-offset: -2px;
}

/* 4-P1-5: 多选 checkbox */
.fav-checkbox {
  display: flex;
  align-items: center;
  padding-top: 2px;
  cursor: pointer;
}
.fav-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-brand);
}

/* ==================== 5-P1-2 (后缀): 文件夹 ==================== */

/* 文件夹 chip 行: 横向滚动 */
.fav-folder-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0 8px;
  overflow-x: auto;
  scrollbar-width: thin;
  flex-wrap: nowrap;
}
/* 5-P2 (后缀): 标签 chip 行 (跟文件夹同结构, 但用更浅的背景区分) */
.fav-tag-chips {
  padding: 0 0 8px;
}
.fav-tag-chip {
  background: color-mix(in srgb, var(--folder-color, #5c6ef5) 5%, transparent);
}
.fav-folder-chips::-webkit-scrollbar {
  height: 4px;
}
.fav-folder-chips::-webkit-scrollbar-thumb {
  background: var(--color-border, #e5e7eb);
  border-radius: 2px;
}

.fav-folder-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 16px;
  border: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-bg-card, #fff);
  color: var(--color-text-secondary, #6b7280);
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
  flex-shrink: 0;
}
.fav-folder-chip:hover {
  border-color: var(--folder-color, var(--color-brand));
  color: var(--folder-color, var(--color-brand));
}
.fav-folder-chip.active {
  background: var(--folder-color, var(--color-brand));
  color: #fff;
  border-color: var(--folder-color, var(--color-brand));
}
.fav-folder-chip.active .fav-folder-count {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}
.fav-folder-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--color-bg-page, #f3f4f6);
  color: var(--color-text-secondary, #6b7280);
  font-size: 11px;
  font-weight: 500;
}
.fav-folder-add {
  border-style: dashed;
  color: var(--color-text-tertiary, #9ca3af);
}
.fav-folder-add:hover {
  border-style: solid;
  color: var(--color-brand);
  border-color: var(--color-brand);
}
.fav-folder-manage {
  color: var(--color-text-tertiary, #9ca3af);
}
.fav-folder-manage:hover {
  color: var(--color-text-primary, #111827);
  border-color: var(--color-text-tertiary, #9ca3af);
}

/* 搜索 + 视频筛选行 (从原 .fav-filter-bar 平铺结构改为上下两行) */
.fav-filter-bar {
  margin-bottom: 12px;
}
.fav-search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 文件夹徽章 (卡片内显示) */
.fav-card-folder {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px;
  border-radius: 8px;
  font-size: 11px;
  background: color-mix(in srgb, var(--folder-color) 12%, transparent);
  color: var(--folder-color);
  border: 1px solid color-mix(in srgb, var(--folder-color) 30%, transparent);
}

/* 弹层 (新建文件夹 / 移动 / 管理) */
.fav-modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}
.fav-modal {
  background: var(--color-bg-card, #fff);
  border-radius: 12px;
  padding: 18px;
  min-width: 320px;
  max-width: 90vw;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}
.fav-modal-wide {
  min-width: 400px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}
.fav-modal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--color-text-primary, #111827);
}
.fav-modal-body {
  margin-bottom: 14px;
  max-height: 50vh;
  overflow-y: auto;
}
.fav-modal-label {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 6px;
  margin-top: 8px;
}
.fav-modal-label:first-child {
  margin-top: 0;
}
.fav-modal-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  font-size: 14px;
  background: var(--color-bg-page, #f9fafb);
  color: var(--color-text-primary, #111827);
  outline: none;
  box-sizing: border-box;
}
.fav-modal-input:focus {
  border-color: var(--color-brand);
  background: #fff;
}
.fav-modal-error {
  margin-top: 8px;
  font-size: 12px;
  color: #ef4444;
}
.fav-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 颜色选择器 */
.fav-color-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.fav-color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  transition: transform var(--sf-duration-fast);
}
.fav-color-dot:hover {
  transform: scale(1.1);
}
.fav-color-dot.active {
  border-color: #111827;
  box-shadow: 0 0 0 2px #fff inset;
}

/* 文件夹选择 (per-card 用) */
.fav-move-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.fav-move-check {
  margin-left: auto;
  color: var(--color-brand);
}
.folder-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dropdown-divider {
  height: 1px;
  background: var(--color-border, #e5e7eb);
  margin: 4px 0;
}

/* 批量移动菜单 */
.folder-picker-menu {
  min-width: 180px;
  max-height: 320px;
  overflow-y: auto;
}
.folder-pick-count {
  margin-left: auto;
  font-size: 11px;
  color: var(--color-text-tertiary, #9ca3af);
}

/* 文件夹管理列表 */
.fav-manage-list {
  padding: 0;
}
.fav-manage-empty {
  padding: 20px;
  text-align: center;
  color: var(--color-text-tertiary, #9ca3af);
  font-size: 13px;
}
.fav-manage-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 4px;
  border-bottom: 1px solid var(--color-border, #f3f4f6);
  transition: background var(--sf-duration-fast);
}
.fav-manage-row:last-child {
  border-bottom: none;
}
.fav-manage-row.fav-drag-over {
  background: color-mix(in srgb, var(--color-brand) 8%, transparent);
  border-top: 2px solid var(--color-brand);
}
.fav-drag-handle {
  color: var(--color-text-tertiary, #9ca3af);
  cursor: grab;
  flex-shrink: 0;
}
.fav-drag-handle:active {
  cursor: grabbing;
}
.fav-manage-tip {
  font-size: 11px;
  color: var(--color-text-tertiary, #9ca3af);
  font-weight: normal;
  margin-left: auto;
}
.fav-manage-name {
  flex: 1;
  font-size: 14px;
  color: var(--color-text-primary, #111827);
}
.fav-manage-count {
  font-size: 12px;
  color: var(--color-text-tertiary, #9ca3af);
}

/* 弹层过渡 */
.fav-modal-enter-active, .fav-modal-leave-active {
  transition: opacity var(--sf-duration-normal) var(--sf-ease-standard);
}
.fav-modal-enter-from, .fav-modal-leave-to {
  opacity: 0;
}
.fav-modal-enter-active .fav-modal,
.fav-modal-leave-active .fav-modal {
  transition: transform var(--sf-duration-normal) var(--sf-ease-standard);
}
.fav-modal-enter-from .fav-modal,
.fav-modal-leave-to .fav-modal {
  transform: scale(0.95) translateY(-10px);
}

/* P2-6 (UI 统一): 重命名文件夹弹窗 */
.fav-rename-body {
  padding: 8px 0;
}
.fav-rename-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}
.fav-rename-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  margin: 6px 0 0 0;
}

/* 5-P2 (后缀): 导出提示 */
.fav-export-hint {
  cursor: default;
  opacity: 0.75;
}
.fav-export-hint:hover {
  background: transparent;
}
.fav-export-hint-text {
  font-size: 11px;
  color: var(--color-text-tertiary, #9ca3af);
  white-space: nowrap;
}

/* 4-P1-5: 批量操作工具栏 */
.fav-batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-bottom: 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-brand);
  border-radius: 10px;
  position: sticky;
  top: 0;
  z-index: 5;
}
.fav-batch-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-brand);
  flex: 1;
}
.fav-bar-enter-active, .fav-bar-leave-active {
  transition: opacity var(--sf-duration-normal), transform var(--sf-duration-normal);
}
.fav-bar-enter-from, .fav-bar-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.subtitle-fav-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  opacity: 0;
  transition: opacity var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.subtitle-fav-card:hover {
  border-color: var(--color-brand-bright);
  box-shadow: var(--shadow-sm);
}

.subtitle-fav-card:hover::before {
  opacity: 1;
}

.fav-card-content {
  flex: 1;
  min-width: 0;
}

.fav-card-english {
  font-size: var(--text-base, 15px);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: 6px;
}

.fav-card-chinese {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 10px;
  font-style: italic;
}

.fav-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.fav-card-category :deep(.sf-tag) {
  font-size: 11px;
}

.fav-card-duration {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.fav-practice-count {
  font-size: 11px;
  color: #fff;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  padding: 2px 10px;
  border-radius: var(--radius-full, 9999px);
  font-weight: 500;
}

.fav-card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.fav-more-icon {
  font-size: 16px;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 10px;
  border-radius: var(--radius-md, 12px);
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.fav-more-icon:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.fav-practice-btn {
  font-size: var(--text-sm, 13px);
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border-color: var(--color-brand-bright) !important;
  min-height: 44px;
}

.fav-practice-btn:hover {
  background: var(--color-brand-hover) !important;
  border-color: var(--color-brand-hover) !important;
}

.practice-arrow {
  margin-left: 2px;
}

/* ====== Vocabulary list ====== */
.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vocab-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  padding: 20px;
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  position: relative;
}

.vocab-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--color-accent);
  opacity: 0;
  transition: opacity var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.vocab-card:hover {
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

.vocab-card:hover::before {
  opacity: 1;
}

.vocab-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.vocab-content {
  flex: 1;
  min-width: 0;
}

.vocab-word-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.vocab-word {
  font-size: var(--text-lg, 18px);
  font-weight: 700;
  color: var(--color-text-primary);
}

.vocab-phonetic {
  font-size: var(--text-sm, 13px);
  color: var(--color-text-secondary);
  font-style: italic;
}

.vocab-speak-btn {
  width: 32px !important;
  height: 32px !important;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border-color: var(--color-brand-bright) !important;
  color: #fff !important;
  min-height: 44px !important;
  min-width: 44px !important;
}

.vocab-speak-btn:hover {
  background: var(--color-brand-hover) !important;
  border-color: var(--color-brand-hover) !important;
}

.vocab-translation {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.vocab-context {
  /* 5-P0 (UI 统一): 引用条样式 - 左侧 3px 主色 border, 背景 elevated, 引号 */
  font-size: var(--text-xs, 12px);
  color: var(--color-text-secondary);
  line-height: 1.5;
  background: var(--color-bg-elevated);
  padding: 8px 12px;
  border-left: 3px solid var(--color-brand);
  border-radius: 0 var(--radius-sm, 8px) var(--radius-sm, 8px) 0;
  display: inline-block;
  font-style: italic;
}

.context-label {
  font-weight: 500;
  color: var(--color-text-muted);
  font-style: normal;
}

.vocab-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* ====== Pagination ====== */
.pagination {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

/* ====== Dropdown items ====== */
:deep(.dropdown-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary);
  cursor: pointer;
  border-radius: var(--radius-sm, 8px);
  transition: background var(--sf-duration-fast);
  min-height: 44px;
}

:deep(.dropdown-item:hover) {
  background: var(--color-bg-elevated);
}

/* ====== 5-P1-2: 笔记展示/编辑 ====== */
.fav-card-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(245, 158, 11, 0.08);  /* 琥珀色淡背景, 跟"笔记"语义匹配 */
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-text-primary);
  border-left: 3px solid var(--color-warm, #F59E0B);
}
.note-icon {
  color: var(--color-warm, #F59E0B);
  flex-shrink: 0;
}
.note-text {
  flex: 1;
  line-height: 1.5;
  word-break: break-word;
}
.note-edit-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.note-edit-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-text-primary);
}

.fav-card-note-edit {
  margin: 8px 0;
}
.note-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-family: inherit;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  min-height: 60px;
  box-sizing: border-box;
}
.note-textarea:focus {
  outline: none;
  border-color: var(--color-brand, #2563EB);
}
.note-edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 6px;
}

.fav-card-note-add {
  margin: 4px 0 8px 0;
}

/* ====== 5-P1-2: 用户标签 chips ====== */
.fav-card-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin: 4px 0 8px 0;
}
.user-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 4px 1px 8px;
  font-size: 11px;
  line-height: 18px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 12%, transparent);
  color: var(--tag-color, #5c6ef5);
  border: 1px solid color-mix(in srgb, var(--tag-color, #5c6ef5) 30%, transparent);
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
}
.user-tag-chip:hover {
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 18%, transparent);
}
.user-tag-name {
  font-weight: 500;
}
.user-tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: none;
  background: transparent;
  color: inherit;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  border-radius: 50%;
  opacity: 0.5;
  padding: 0;
  transition: opacity var(--sf-duration-fast) var(--sf-ease-standard), background var(--sf-duration-fast) var(--sf-ease-standard);
}
.user-tag-remove:hover {
  opacity: 1;
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 25%, transparent);
}
.add-tag-btn {
  border: 1px dashed var(--color-border, #cbd5e1);
  background: transparent;
  color: var(--color-text-secondary, #64748b);
  font-size: 11px;
  line-height: 18px;
  padding: 1px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
}
.add-tag-btn:hover {
  border-color: var(--color-primary, #5c6ef5);
  color: var(--color-primary, #5c6ef5);
  background: rgba(92, 110, 245, 0.06);
}
.add-tag-input-wrap {
  display: inline-flex;
}
.add-tag-input {
  border: 1px solid var(--color-primary, #5c6ef5);
  background: var(--color-bg-card, #fff);
  color: var(--color-text-primary, #1e293b);
  font-size: 12px;
  line-height: 18px;
  padding: 1px 8px;
  border-radius: 10px;
  outline: none;
  width: 140px;
}
.add-tag-input:focus {
  box-shadow: 0 0 0 2px rgba(92, 110, 245, 0.15);
}
/* TransitionGroup for tag chips */
.tag-chip-enter-active, .tag-chip-leave-active {
  transition: all var(--sf-duration-normal) var(--sf-ease-standard);
}
.tag-chip-enter-from {
  opacity: 0;
  transform: scale(0.8);
}
.tag-chip-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* ====== 5-P1-1: 视频收藏 Tab ====== */
.fav-videos-tab {
  padding: 4px 0;
}

.video-fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

.video-fav-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--sf-duration-normal), box-shadow var(--sf-duration-normal);
  position: relative;
}
.video-fav-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.video-cover {
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--color-bg-elevated);
  position: relative;
  overflow: hidden;
}
.video-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.video-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}
.video-duration {
  position: absolute;
  right: 8px;
  bottom: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.video-info {
  padding: 12px;
}
.video-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}
.video-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.video-fav-time {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.video-remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--sf-duration-normal), background var(--sf-duration-normal);
}
.video-fav-card:hover .video-remove-btn {
  opacity: 1;
}
.video-remove-btn:hover {
  background: var(--color-danger, #ef4444);
}

/* 5-P1-1: 视频骨架屏 (复用 P2-2 通用骨架样式) */
.video-skeleton-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}
.video-skeleton-card {
  aspect-ratio: 16/9;
  background: linear-gradient(90deg, var(--color-bg-elevated) 25%, #e5e7eb 50%, var(--color-bg-elevated) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-lg, 16px);
  animation: skeleton-shimmer 1.5s infinite;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ====== Mobile responsive ====== */
@media (max-width: 768px) {
  .yt-favorites {
    max-width: 100%;
  }

  .fav-page-header {
    padding: 8px 0 16px;
  }

  .fav-page-title {
    font-size: var(--text-xl, 20px);
  }

  .fav-tabs {
    gap: 24px;
  }

  /* Phase 3 (H5): H5 端隐藏视频收藏 tab, 只剩 字幕 + 单词短语 */
  .fav-tab--desktop {
    display: none;
  }

  .fav-tab {
    font-size: var(--text-sm, 14px);
  }

  .subtitle-fav-card {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }

  .subtitle-fav-card::before {
    display: none;
  }

  .fav-card-actions {
    width: 100%;
    justify-content: space-between;
    padding-top: 12px;
    border-top: 1px solid var(--color-border);
  }

  .fav-card-english {
    font-size: var(--text-sm, 14px);
  }

  .fav-card-chinese {
    font-size: var(--text-xs, 13px);
  }

  .vocab-card {
    padding: 16px;
  }

  .vocab-card::before {
    display: none;
  }

  .vocab-word {
    font-size: var(--text-base, 16px);
  }

  /* Phase 3 (H5): 移动端 vocab 卡片"去练习"按钮更紧凑 */
  .vocab-practice-btn {
    padding: 4px 10px;
    font-size: 12px;
  }
  .vocab-actions {
    flex-direction: column;
    gap: 6px;
    align-items: flex-end;
  }
}

@media (max-width: 480px) {
  .fav-page-header {
    gap: 8px;
  }

  .fav-page-title {
    font-size: var(--text-lg, 18px);
  }

  .fav-manage-btn {
    font-size: var(--text-xs, 12px);
    padding: 6px 12px;
  }

  .fav-tabs {
    gap: 16px;
  }

  .fav-tab {
    font-size: var(--text-xs, 13px);
    padding: 10px 2px;
  }

  .subtitle-fav-card {
    padding: 14px;
  }

  .fav-card-meta {
    flex-wrap: wrap;
    gap: 6px;
  }

  .fav-more-icon {
    padding: 10px;
    min-width: 44px;
    min-height: 44px;
  }

  .vocab-speak-btn {
    min-width: 44px !important;
    min-height: 44px !important;
  }

  .vocab-context {
    font-size: 11px;
  }

  /* P2-6: 移动端隐藏"未练习"标签 */
  .fav-practice-zero-mobile-hidden {
    display: none;
  }
}

/* ================================================
   P2 增量 — Favorites 微迭代样式
   P2-5: 刷新按钮移到 Tab 行右侧
   P2-3: 视频封面缩略图 (懒加载)
   P2-2: 骨架屏
   P2-4: 最后练习时间 + 快速复习按钮
   ================================================ */

/* P2-5: Tabs + Refresh 同排 */
.fav-tabs-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 2px solid var(--color-border);
  margin-bottom: 28px;
}

.fav-tabs-row .fav-tabs {
  border-bottom: none;  /* row 已统一管理下划线 */
  margin-bottom: 0;
  padding-bottom: 0;
}

.fav-refresh-btn {
  width: 36px;
  height: 36px;
  min-height: 36px;
  padding: 0;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: 50%;
  flex-shrink: 0;
  margin-bottom: 6px;  /* 跟 tab 基线对齐 */
  transition: all var(--sf-duration-normal, 220ms) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-refresh-btn:hover {
  color: var(--color-brand-bright);
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

.fav-refresh-btn svg {
  animation: fav-refresh-spin 0.6s linear;
}

.fav-refresh-btn.is-loading svg {
  animation: fav-refresh-spin 1s linear infinite;
}

@keyframes fav-refresh-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* P2-3: 视频封面缩略图 (懒加载, 圆形柔和, hover scale) */
.fav-card-thumb {
  width: 96px;
  height: 64px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  transition: transform var(--sf-duration-normal, 220ms) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1)),
              border-color var(--sf-duration-normal, 220ms) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-card-thumb:hover {
  transform: scale(1.04);
  border-color: var(--color-brand-bright);
}

.fav-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* P2-2: 骨架屏 (loading 占位) */
.skeleton-fav-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 16px);
  margin-bottom: 10px;
}

.sk-line {
  height: 12px;
  background: linear-gradient(
    90deg,
    var(--color-bg-elevated) 0%,
    rgba(0, 0, 0, 0.06) 50%,
    var(--color-bg-elevated) 100%
  );
  background-size: 200% 100%;
  border-radius: 6px;
  animation: sk-shimmer 1.4s ease-in-out infinite;
}

.sk-title {
  width: 70%;
  height: 16px;
}

.sk-sub {
  width: 85%;
  height: 12px;
}

.sk-meta {
  width: 40%;
  height: 10px;
  margin-top: 4px;
}

@keyframes sk-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* P2-4: 快速复习按钮 (旋转图标, ghost 风格) */
.fav-quick-practice-btn {
  width: 32px;
  height: 32px;
  min-height: 32px;
  padding: 0;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  background: transparent;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all var(--sf-duration-normal, 220ms) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-quick-practice-btn:hover {
  color: var(--color-brand-bright);
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
  transform: rotate(-90deg);
}

.fav-quick-practice-btn:active {
  transform: rotate(-180deg) scale(0.92);
}

/* P2-4: "未练习" 灰色标签 */
.fav-practice-zero {
  background: transparent !important;
  color: var(--color-text-muted) !important;
  border: 1px dashed var(--color-border);
  padding: 2px 10px;
  cursor: default;
}
</style>
