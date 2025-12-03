<template>
  <div class="course-store-wrapper">
    <div class="store-header">
      <h1>Course Store</h1>
      <p>Browse all available courses in the platform</p>
      <div class="actions-row">
        <input v-model="search" type="text" placeholder="Search courses..." class="search-input" />
        <button class="ai-reco-btn" @click="openRecoModal">AI Course Recommendation</button>
      </div>
    </div>

    <div class="store-layout">
      <!-- Left: Persistent Filter Sidebar -->
      <aside class="filters-sidebar">
        <div class="filters-card">
          <h4>Filters</h4>
          <div class="filter-section">
            <label>Level</label>
            <select v-model="levelFilter">
              <option value="">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div class="filter-section">
            <label>Category</label>
            <select v-model="categoryFilter">
              <option value="">All Categories</option>
              <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="filter-section">
            <label>Topic</label>
            <select v-model="topicFilter">
              <option value="">All Topics</option>
              <option v-for="t in filteredAvailableTopics" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="filter-actions">
            <button class="apply-btn" @click="applyFilters">Apply</button>
            <button class="reset-btn" @click="resetFilters">Reset</button>
          </div>
        </div>
      </aside>

      <!-- Right: Courses -->
      <section class="store-content">
        <div v-if="loading" class="loading"><span>Loading courses...</span></div>
        <div v-else class="courses-grid">
          <div v-for="c in paginatedCourses" :key="c.id" class="course-card">
            <h3 class="title">{{ c.title }}</h3>
            <p class="instructor" v-if="c.instructorName">By {{ c.instructorName }}</p>
            <p class="desc" v-if="c.description">{{ truncate(c.description,140) }}</p>
            <div class="meta">
              <span class="badge level">{{ c.level || 'beginner' }}</span>
              <span v-if="c.category" class="badge cat">{{ c.category }}</span>
              <span v-if="c.topic" class="badge topic">{{ c.topic }}</span>
            </div>
            <div class="price-row">
              <span class="price" v-if="c.price">{{ formatPrice(c.price, c.currency) }}</span>
              <span v-else class="price free">Free</span>
            </div>
            <div class="actions">
              <template v-if="!isEnrolled(c.id)">
                <button
                  v-if="!c.price || c.price === 0"
                  class="btn-enroll"
                  @click="enroll(c)"
                  :disabled="enrollingIds.has(c.id)"
                >
                  {{ enrollingIds.has(c.id)? 'Enrolling...' : 'Enroll' }}
                </button>
                <button
                  v-else
                  class="btn-enroll btn-buy"
                  @click="openPayment(c)"
                  :disabled="enrollingIds.has(c.id)"
                >
                  {{ enrollingIds.has(c.id)? 'Processing...' : 'Buy' }}
                </button>
              </template>
              <button v-else class="btn-enroll" disabled>Enrolled</button>
            </div>
          </div>
          <div v-if="!filteredCourses.length" class="empty">No courses found.</div>
        </div>
        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage===1" @click="setPage(currentPage-1)">Prev</button>
          <template v-for="item in displayedPages">
            <span v-if="item.type==='ellipsis'" :key="item.key + '-e'" class="page-ellipsis">…</span>
            <button
              v-else
              :key="item.key + '-p'"
              class="page-btn"
              :class="{ active: item.num===currentPage }"
              @click="setPage(item.num)"
            >{{ item.num }}</button>
          </template>
          <button class="page-btn" :disabled="currentPage===totalPages" @click="setPage(currentPage+1)">Next</button>
        </div>
      </section>
    </div>

    <!-- Payment Modal -->
    <div class="modal fade" id="paymentModal" tabindex="-1" ref="paymentModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <span v-if="paymentStep==='info'">Course Information</span>
              <span v-else>Payment - Scan QR Code</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetPayment"></button>
          </div>

          <!-- Step: Info -->
          <div v-if="paymentStep==='info'" class="modal-body">
            <div v-if="selectedCourse" class="modal-course-info">
              <h6>{{ selectedCourse.title }}</h6>
              <p class="course-meta">{{ selectedCourse.instructorName || 'N/A' }} · {{ selectedCourse.level || 'beginner' }}</p>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">Status</span>
                  <span class="info-value">{{ selectedCourse.isPublic? 'Public':'Private' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Price</span>
                  <span class="info-value">{{ formatPrice(selectedCourse.price, selectedCourse.currency) }}</span>
                </div>
              </div>
              <div class="modal-actions">
                <button v-if="selectedCourse.price==0" class="action-button" @click="enroll(selectedCourse)">Enroll Now</button>
                <button v-else class="action-button" @click="proceedToQR">Proceed to Payment</button>
              </div>
            </div>
          </div>

          <!-- Step: QR -->
          <div v-else class="modal-body text-center">
            <div v-if="selectedCourse" class="qr-section">
              <h6>{{ selectedCourse.title }}</h6>
              <p class="payment-amount">Amount: <strong>{{ formatPrice(selectedCourse.price, selectedCourse.currency) }}</strong></p>
              <div class="qr-code"><img :src="qrUrl" alt="QR" /></div>
              <p class="qr-instruction">Scan the QR code to complete payment. Use Confirm Payment after paying.</p>
              <div v-if="isChecking" class="checking-status">Checking payment status...</div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="action-button secondary" data-bs-dismiss="modal" @click="resetPayment">Close</button>
            <button v-if="paymentStep==='qr'" class="action-button test-purchase" @click="testPurchase">Test Purchase</button>
            <button v-if="paymentStep==='qr'" class="action-button" @click="confirmPaid">Confirm Payment</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendation Modal -->
    <div class="modal fade" id="recoModal" tabindex="-1" ref="recoModal">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content ai-modal">
          <div class="modal-header">
            <h5 class="modal-title">AI Course Recommendation</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetReco"></button>
          </div>
          <div class="modal-body">
            <div class="reco-layout">
              <!-- Chat Column -->
              <div class="chat-column">
                <div class="chat-window" ref="chatWindow">
                  <div v-for="(m,i) in recoMessages" :key="i" class="msg" :class="m.role">
                    <div class="bubble" v-html="formatMessage(m.text)"></div>
                  </div>
                  <div v-if="recoLoading" class="msg assistant"><div class="bubble">Đang suy nghĩ...</div></div>
                </div>
                <form class="chat-input-row" @submit.prevent="sendRecoInput">
                  <input v-model="recoInput" :placeholder="recoPlaceholder" class="chat-input" />
                  <button class="send-btn" :disabled="recoLoading || !recoInput.trim()">{{ recoLoading? '...' : 'Send' }}</button>
                </form>
                
              </div>
              <!-- Recommendations Column -->
              <div class="courses-column">
                <div class="panel-header">
                  <h6>Recommended Courses</h6>
                  <small v-if="!recoCompleted">Chat with AI to get suggestions</small>
                  <small v-else-if="!recoCourses.length">No courses matched this turn.</small>
                </div>
                <div v-if="recoLoading && !recoCompleted" class="panel-loading">Thinking...</div>
                <div v-else class="reco-courses-list">
                  <div v-for="c in recoCourses" :key="c.id" class="r-course" :class="{ semantic: c.semantic }">
                    <h6>{{ c.title }}</h6>
                    <p v-if="c.description" class="r-desc">{{ truncate(c.description,110) }}</p>
                    <div class="r-tags">
                      <span v-for="cat in c.categories" :key="cat" class="tag cat">{{ cat }}</span>
                      <span v-for="t in c.topics" :key="t" class="tag topic">{{ t }}</span>
                    </div>
                    <div class="r-meta">
                      <span class="lvl">{{ c.level }}</span>
                      <span class="price" v-if="c.price">{{ formatPrice(c.price, c.currency) }}</span>
                      <span class="price free" v-else>Free</span>
                    </div>
                    <p v-if="c.reason" class="reason">{{ c.reason }}</p>
                    <div class="r-actions">
                      <button v-if="!isEnrolled(c.id)" class="mini-enroll" @click="enroll(c)" :disabled="enrollingIds.has(c.id)">
                        {{ enrollingIds.has(c.id)?'Enrolling...':'Enroll' }}
                      </button>
                      <button v-else class="mini-enroll enrolled" disabled>Enrolled</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="action-button secondary" data-bs-dismiss="modal" @click="onCloseReco">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getStoredSession } from '../../services/authService'

export default {
  name: 'StudentCourseStore',
  data() {
    return {
      loading: true,
      courses: [],
      myCourseIds: new Set(),
      enrollingIds: new Set(),
      search: '',
      levelFilter: '',
      // payment state
      selectedCourse: null,
      paymentStep: 'info',
      isChecking: false,
      qrUrl: '',
      paymentInterval: null,
      // filter state
      showFilterPanel: false, // no longer used, kept for compatibility
      categoryFilter: '',
      topicFilter: '',
      availableCategories: [],
      availableTopics: [],
      // AI recommendation state
      recoMessages: [],
      recoInput: '',
      recoLoading: false,
      recoCourses: [],
      recoCompleted: false,
      chatSessionId: null,
      followUp: null,
      // pagination
      currentPage: 1,
      pageSize: 6,
    }
  },
  computed: {
    // Keep search filtering client-side; server already filtered by chosen params
    filteredCourses() {
      const term = this.search.trim().toLowerCase()
      return this.courses.filter(c => {
        if (term && !(c.title||'').toLowerCase().includes(term) && !(c.description||'').toLowerCase().includes(term)) return false
        return true
      })
    },
    filteredAvailableTopics() {
      if (!this.categoryFilter) return this.availableTopics
      const categoryLC = this.categoryFilter.toLowerCase()
      const topicSet = new Set()
      this.courses.forEach(c => {
        const catArr = (Array.isArray(c.categoriesArr) ? c.categoriesArr : (c.category ? [c.category] : []))
          .map(x => (x || '').toLowerCase())
        if (catArr.includes(categoryLC)) {
          const tops = Array.isArray(c.topicsArr) ? c.topicsArr : (c.topic ? [c.topic] : [])
          tops.forEach(t => { if (t) topicSet.add(t) })
        }
      })
      const result = Array.from(topicSet).sort()
      return result.length ? result : this.availableTopics
    },
    recoPlaceholder(){
      return 'Nhập câu hỏi hoặc level/category/topic (tùy chọn)'
    },
    paginatedCourses(){
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredCourses.slice(start, start + this.pageSize)
    },
    totalPages(){
      const total = this.filteredCourses.length
      return total ? Math.ceil(total / this.pageSize) : 1
    },
    displayedPages(){
      const pages = []
      const total = this.totalPages
      const current = this.currentPage
      if(total <= 10){
        for(let i=1;i<=total;i++) pages.push({ type:'page', num:i, key:'p'+i })
        return pages
      }
      const windowSize = 2 // pages before/after current
      const start = Math.max(2, current - windowSize)
      const end = Math.min(total - 1, current + windowSize)
      // Always show first page
      pages.push({ type:'page', num:1, key:'p1' })
      if(start > 2){ pages.push({ type:'ellipsis', key:'e-start' }) }
      for(let i=start;i<=end;i++){
        pages.push({ type:'page', num:i, key:'p'+i })
      }
      if(end < total - 1){ pages.push({ type:'ellipsis', key:'e-end' }) }
      pages.push({ type:'page', num: total, key:'p'+total })
      return pages
    },
    pageButtons(){
      const total = this.totalPages
      const current = this.currentPage
      const windowSize = 6
      const buttons = []
      if(total <= windowSize + 2){
        // show all pages directly
        for(let i=1;i<=total;i++) buttons.push({ type:'page', number:i, key:'p'+i })
        return buttons
      }
      let start = Math.max(1, current - Math.floor(windowSize/2))
      let end = start + windowSize - 1
      if(end > total){ end = total; start = end - windowSize + 1 }
      if(start > 1){
        buttons.push({ type:'page', number:1, key:'p1' })
        if(start > 2) buttons.push({ type:'ellipsis', key:'e-start' })
      }
      for(let i=start;i<=end;i++){
        buttons.push({ type:'page', number:i, key:'p'+i })
      }
      if(end < total){
        if(end < total - 1) buttons.push({ type:'ellipsis', key:'e-end' })
        buttons.push({ type:'page', number: total, key:'p'+total })
      }
      return buttons
    },
  },
  watch: {
    categoryFilter() { this.topicFilter = '' },
    search(){ this.currentPage = 1 },
    levelFilter(){ this.currentPage = 1 },
    categoryFilter(){ this.currentPage = 1 },
    topicFilter(){ this.currentPage = 1 },
  },
  async mounted() {
    await this.loadAll()
  },
  methods: {
    authHeaders() {
      const s = getStoredSession();
      return s?.access_token ? { Authorization: `Bearer ${s.access_token}` } : {}
    },
    async loadAll(params = {}) {
      this.loading = true
      try {
        const allRes = await axios.get('http://localhost:5000/api/student/courses', { params })
        const list = Array.isArray(allRes.data?.courses) ? allRes.data.courses : []
        this.courses = list.map(c => ({
          ...c,
          instructorName: c.instructorName || c.instructor_name || null,
          category: Array.isArray(c.categories) && c.categories.length ? c.categories[0] : c.category || null,
          topic: Array.isArray(c.topics) && c.topics.length ? c.topics[0] : c.topic || null,
          categoriesArr: Array.isArray(c.categories) ? c.categories : [],
          topicsArr: Array.isArray(c.topics) ? c.topics : [],
        }))
        const catSet = new Set()
        const topicSet = new Set()
        this.courses.forEach(c => {
          c.categoriesArr.forEach(cat => catSet.add(cat))
          c.topicsArr.forEach(t => topicSet.add(t))
        })
        this.availableCategories = Array.from(catSet).sort()
        this.availableTopics = Array.from(topicSet).sort()
        try {
          const mineRes = await axios.get('http://localhost:5000/api/student/my-courses', { headers: this.authHeaders() })
          const mine = mineRes.data?.courses || []
          this.myCourseIds = new Set(mine.map(m => m.id))
        } catch { this.myCourseIds = new Set() }
      } catch (e) { console.error('Failed loading courses', e) } finally { this.loading = false }
    },
    isEnrolled(id) { return this.myCourseIds.has(id) },
    formatPrice(p,c) { try { return (!p||p===0)? 'Free' : new Intl.NumberFormat('en-US',{style:'currency',currency: c||'USD'}).format(p) } catch { return p } },
    truncate(t,max) { if(!t) return ''; return t.length>max? t.slice(0,max-1)+'…':t },
    async enroll(course) {
      if (!course?.id || this.isEnrolled(course.id)) return
      this.enrollingIds.add(course.id)
      try {
        const res = await axios.post('http://localhost:5000/api/student/register', { courseId: course.id }, { headers: this.authHeaders() })
        if (res.data?.success) {
          this.myCourseIds.add(course.id)
          // Close payment modal if open
          this.closeModal()
        }
      } catch (e) {
        const status = e?.response?.status
        if (status === 401) {
          // Graceful handling: prompt and redirect to login
          alert('Please log in to enroll in courses.')
          this.$router.push({ name: 'Login' }).catch(()=>{})
        } else {
          console.error('Enroll failed', e)
          alert('Enroll failed')
        }
      } finally {
        this.enrollingIds.delete(course.id)
      }
    },
    openCourse(c) { if (!c?.id) return; this.$router.push({ name: 'StudentCourseLesson', params: { courseId: c.id } }).catch(()=>{}) },
    // Payment flow
    openPayment(course) {
      this.selectedCourse = course
      this.paymentStep = 'info'
      const modal = this.ensureModal()
      modal.show()
    },
    proceedToQR() {
      if(!this.selectedCourse) return
      this.paymentStep = 'qr'
      this.qrUrl = this.makeQrUrl(this.selectedCourse)
      const modal = this.ensureModal()
      modal.show()
      this.startPaymentCheck()
    },
    makeQrUrl(course) {
      const data = encodeURIComponent(`COURSE:${course.slug||course.id}|AMOUNT:${course.price}${course.currency||'USD'}`)
      return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${data}`
    },
    startPaymentCheck() {
      // Placeholder for future real-time payment status polling
      this.isChecking = false
    },
    testPurchase() {
      if (!this.selectedCourse) return
      this.enroll(this.selectedCourse) // direct enroll for test
    },
    confirmPaid() {
      if (!this.selectedCourse) return
      // After user confirms payment, call enroll
      this.enroll(this.selectedCourse)
    },
    resetPayment() {
      this.paymentStep = 'info'
      this.isChecking = false
      this.qrUrl = ''
      this.selectedCourse = null
      if (this.paymentInterval) { clearInterval(this.paymentInterval); this.paymentInterval = null }
    },
    ensureModal() {
      // bootstrap assumed global (included in index.html)
      let modal = window.bootstrap?.Modal.getInstance(this.$refs.paymentModal)
      if (!modal && window.bootstrap) modal = new window.bootstrap.Modal(this.$refs.paymentModal)
      return modal
    },
    closeModal() {
      const modal = window.bootstrap?.Modal.getInstance(this.$refs.paymentModal)
      if (modal) modal.hide()
      this.resetPayment()
    },
    // Remove open/close panel methods (not used), keep no-op for safety
    openFilterPanel() { this.showFilterPanel = true },
    closeFilterPanel() { this.showFilterPanel = false },
    resetFilters() {
      this.levelFilter = ''
      this.categoryFilter = ''
      this.topicFilter = ''
      this.applyFilters()
    },
    async applyFilters() {
      const params = {}
      if (this.levelFilter) params.level = this.levelFilter
      if (this.categoryFilter) params.category = this.categoryFilter
      if (this.topicFilter) params.topic = this.topicFilter
      await this.loadAll(params)
      this.closeFilterPanel()
    },
    // ---------- Chat persistence ----------
    storageKey(){ return 'ai_reco_chat_v1' },
    saveRecoState(){
      try{
        const payload = {
          chatSessionId: this.chatSessionId,
          recoMessages: this.recoMessages,
          recoCourses: this.recoCourses,
          recoCompleted: this.recoCompleted,
          followUp: this.followUp,
          savedAt: Date.now()
        }
        localStorage.setItem(this.storageKey(), JSON.stringify(payload))
      }catch{}
    },
    loadRecoState(){
      try{
        const raw = localStorage.getItem(this.storageKey())
        if(!raw) return false
        const s = JSON.parse(raw)
        this.chatSessionId = s.chatSessionId || null
        this.recoMessages = Array.isArray(s.recoMessages)? s.recoMessages : []
        this.recoCourses = Array.isArray(s.recoCourses)? s.recoCourses : []
        this.recoCompleted = !!s.recoCompleted
        this.followUp = s.followUp || null
        this.$nextTick(()=>this.scrollChatBottom())
        return true
      }catch{ return false }
    },
    onCloseReco(){
      // Do not reset; persist current chat
      this.saveRecoState()
    },
    ensureRecoModal(){
      // Create / get Bootstrap modal instance for AI recommendation
      let modal = window.bootstrap?.Modal.getInstance(this.$refs.recoModal)
      if(!modal && window.bootstrap){ modal = new window.bootstrap.Modal(this.$refs.recoModal) }
      return modal
    },
    openRecoModal(){
      // Try restore existing chat; if none, start fresh
      const restored = this.loadRecoState()
      if(!restored){
        this.resetReco()
        this.initRecoChat()
      }
      const m = this.ensureRecoModal(); m && m.show()
    },
    resetReco(){
      this.recoMessages = []
      this.recoInput = ''
      this.recoLoading = false
      this.recoCourses = []
      this.recoCompleted = false
      this.chatSessionId = null
      this.followUp = null
      // Do not clear localStorage here intentionally
    },
    async initRecoChat(){
      try{
        const res = await axios.post('http://localhost:5000/api/student/recommend/chat/init', {}, { headers: this.authHeaders() })
        if(res.data?.success){
          this.chatSessionId = res.data.sessionId
          if(!this.recoMessages.length){
            this.recoMessages.push({ role:'system', text: res.data.message })
            // Optional guidance (not enforced)
            this.recoMessages.push({
              role:'system',
              text:'Bạn có thể (tùy chọn) cung cấp level (beginner/intermediate/advanced), category (vd: web, game dev) và topic (vd: react, c#, solidity) để gợi ý chính xác hơn; hoặc cứ hỏi tự do.'
            })
          }
          this.saveRecoState()
        } else {
          this.recoMessages.push({ role:'assistant', text:'Failed to start AI session.' })
        }
      }catch(e){
        this.recoMessages.push({ role:'assistant', text:'AI service unavailable.' })
      }
    },
    async sendRecoInput(){
      const val = this.recoInput.trim(); if(!val) return
      this.recoMessages.push({ role:'user', text: val })
      this.recoInput=''
      this.saveRecoState()
      await this.sendChatMessage(val)
      this.$nextTick(()=>{ this.scrollChatBottom() })
    },
    async sendChatMessage(message){
      if(!this.chatSessionId){ await this.initRecoChat() }
      this.recoLoading = true
      try{
        if(message.startsWith('/semantic ')){
          const query = message.replace('/semantic ','').trim()
          await this.fetchSemantic(query)
          this.recoMessages.push({ role:'assistant', text:`Semantic suggestions for: ${query}` })
          this.saveRecoState()
          return
        }
        // Backend expects JSON only; avoid form payloads to prevent 415
        const headers = { ...this.authHeaders(), 'Content-Type': 'application/json' }
        const payload = { session_id: this.chatSessionId, text: message }
        let res = await axios.post('http://localhost:5000/api/student/recommend/chat/message', payload, { headers })
        // If API uses camelCase, retry once
        if(!res.data?.success){
          res = await axios.post('http://localhost:5000/api/student/recommend/chat/message', { sessionId: this.chatSessionId, message }, { headers })
        }
        if(!res.data?.success){
          const msg = res.data?.message || res.data?.error || 'Chat failed.'
          this.recoMessages.push({ role:'assistant', text: msg })
          this.saveRecoState();
          return
        }
        const rawReply = res.data.reply || ''
        const cleaned = this.stripJsonBlock(rawReply)
        this.recoMessages.push({ role:'assistant', text: cleaned })
        this.followUp = res.data.followUp || null
        const items = res.data.coursesWithReasons || []
        this.recoCourses = items.map(it => ({
          id: it.course.id,
          title: it.course.title,
          description: it.course.description,
          level: it.course.level,
          price: it.course.price,
          currency: it.course.currency,
          categories: Array.isArray(it.course.categories)? it.course.categories : [],
          topics: Array.isArray(it.course.topics)? it.course.topics : [],
          reason: it.reason
        }))
        if(this.recoCourses.length) this.recoCompleted = true
        this.saveRecoState()
      }catch(e){
        const status = e?.response?.status
        if(status === 401){
          this.recoMessages.push({ role:'assistant', text:'Please log in to use AI recommendations.' })
        }else if(status === 415){
          this.recoMessages.push({ role:'assistant', text:'Unsupported media type. Using JSON payload.' })
        }else if(status === 400){
          this.recoMessages.push({ role:'assistant', text:'Bad request. Please try again.' })
        }else{
          this.recoMessages.push({ role:'assistant', text:'Chat error occurred.' })
        }
        this.saveRecoState()
      }finally{
        this.recoLoading = false
        this.$nextTick(()=>this.scrollChatBottom())
      }
    },
    scrollChatBottom(){
      try{
        const el = this.$refs.chatWindow
        if(el){ el.scrollTop = el.scrollHeight }
      }catch{}
    },
    quickRefine(text){ this.recoInput = text; this.sendRecoInput() },
    acceptFollowUp(){ if(this.followUp){ this.quickRefine(this.followUp) } },
    stripJsonBlock(text){
      try{ return text.replace(/<JSON>[\s\S]*?<\/JSON>/,'').trim() }catch{ return text }
    },
    formatMessage(text){
      // Basic formatting: preserve line breaks
      return (text||'').replace(/\n/g,'<br/>')
    },
    async fetchSemantic(query){
      try{
        this.recoLoading = true
        const res = await axios.post('http://localhost:5000/api/student/recommend/semantic', { query, limit: 6 })
        const list = res.data?.recommendations || []
        this.recoCourses = list.map(c => ({ ...c, reason: 'Semantic match' }))
        this.recoCompleted = true
      }catch(e){
        this.recoMessages.push({ role:'assistant', text:'Semantic recommendation failed.' })
      }finally{ this.recoLoading=false }
    },
    setPage(p){
      if(!p || p<1 || p>this.totalPages) return
      this.currentPage = p
    },
  }
}
</script>

<style scoped>
.course-store-wrapper { --gap:16px; --radius:12px; --border:#e5e7eb; --bg:#f8f9fa; --card-bg:#fff; --text:#111; --muted:#666; --brand:#2563eb; --brand-light:#bfdbfe; background:var(--bg); min-height:100vh; padding:40px; }
.store-header { max-width:1200px; margin:0 auto 24px; display:flex; flex-direction:column; gap:8px; }
.store-header h1 { font-size:32px; font-weight:700; margin:0; color:var(--text); letter-spacing:-.5px; }
.store-header p { margin:0 0 12px; color:var(--muted); font-size:15px; }
.actions-row { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.search-input { flex:1; min-width:260px; padding:12px 16px; border:1px solid var(--border); border-radius:10px; font-size:14px; background:#fff; transition:.2s; }
.search-input:focus { outline:none; border-color:var(--brand); box-shadow:0 0 0 3px rgba(37,99,235,.15); }
.courses-grid { display:grid; gap:var(--gap); grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); align-items:stretch; }
.course-card { background:var(--card-bg); border:1px solid var(--border); border-radius:var(--radius); padding:20px 20px 16px; display:flex; flex-direction:column; position:relative; min-height:265px; box-shadow:0 1px 2px rgba(0,0,0,.04); transition:.2s; }
.course-card:hover { border-color:#d1d5db; box-shadow:0 4px 12px rgba(0,0,0,.06); transform:translateY(-2px); }
.title { font-size:18px; font-weight:600; margin:0 0 4px; color:var(--text); line-height:1.3; }
.instructor{ font-size:12px; color:#555; margin:0 0 6px; }
.desc { font-size:13px; color:var(--muted); margin:0 0 12px; line-height:1.45; display:-webkit-box; -webkit-line-clamp:3; line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.meta { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 8px; }
.badge { font-size:11px; padding:4px 10px; border-radius:8px; font-weight:600; letter-spacing:.5px; line-height:1; user-select:none; }
.badge.level { background:#eef2ff; color:#4338ca; }
.badge.privacy.pub { background:#dcfce7; color:#166534; }
.badge.privacy.priv { background:#fee2e2; color:#991b1b; }
.badge.cat { background:#e0f2fe; color:#075985; }
.badge.topic { background:#fef3c7; color:#92400e; }
.price-row { font-size:15px; font-weight:600; margin:4px 0 12px; }
.price.free { color:#059669; }
.actions { margin-top:auto; }
.btn-enroll, .btn-buy { width:100%; padding:12px 16px; font-size:14px; font-weight:500; border-radius:10px; border:1px solid #93c5fd; background:var(--brand-light); color:#1e3a8a; cursor:pointer; transition:.18s; display:inline-flex; align-items:center; justify-content:center; }
.btn-enroll:hover:not(:disabled), .btn-buy:hover:not(:disabled) { background:var(--brand); color:#fff; border-color:#1d4ed8; }
.btn-enroll:disabled, .btn-buy:disabled { opacity:.6; cursor:not-allowed; }
.loading { padding:60px 20px; text-align:center; color:var(--muted); font-size:15px; }
.empty { grid-column:1/-1; text-align:center; padding:70px 20px; color:var(--muted); font-size:15px; }
/* Modal */
.modal-course-info h6 { font-size:20px; font-weight:600; margin:0 0 6px; }
.modal-course-info .course-meta { font-size:14px; color:var(--muted); margin:0 0 18px; }
.info-list { display:flex; flex-direction:column; gap:10px; margin:0 0 20px; }
.info-row { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid var(--border); }
.info-row:last-child { border-bottom:none; }
.info-label { font-size:13px; color:var(--muted); font-weight:500; }
.info-value { font-size:13px; color:var(--text); font-weight:600; }
.modal-actions { display:flex; justify-content:flex-end; gap:12px; }
.action-button { padding:10px 20px; background:var(--brand); color:#fff; border:none; border-radius:8px; font-size:14px; font-weight:500; cursor:pointer; transition:.18s; }
.action-button:hover { background:#1d4ed8; }
.action-button.secondary { background:#fff; color:#1f2937; border:1px solid var(--border); }
.action-button.secondary:hover { background:#f8f9fa; border-color:#d1d5db; }
.action-button.test-purchase { background:linear-gradient(135deg,#f59e0b,#d97706); color:#fff; }
.action-button.test-purchase:hover { background:linear-gradient(135deg,#d97706,#b45309); }
.qr-section h6 { font-size:16px; font-weight:600; margin:0 0 8px; }
.payment-amount { font-size:14px; color:var(--muted); margin:0 0 20px; }
.payment-amount strong { color:var(--text); font-size:16px; }
.qr-code { margin:20px 0; }
.qr-code img { width:220px; height:220px; border:1px solid var(--border); border-radius:10px; padding:8px; background:#fff; }
.qr-instruction { font-size:13px; color:var(--muted); margin:0 0 14px; }
.checking-status { font-size:14px; color:var(--brand); font-weight:500; }
/* Layout: sidebar + content */
.store-layout { display:grid; grid-template-columns: 300px 1fr; gap:24px; align-items:start; }
.filters-sidebar { position:sticky; top:20px; height:fit-content; }
.filters-card { background:#fff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 4px 16px rgba(0,0,0,.06); padding:18px; display:flex; flex-direction:column; gap:14px; }
.filters-card h4 { font-size:18px; font-weight:600; margin:0 0 4px; color:#111; }
.filter-section { display:flex; flex-direction:column; gap:6px; }
.filter-section label { font-size:12px; font-weight:600; letter-spacing:.5px; color:#555; text-transform:uppercase; }
.filter-section select { padding:10px 12px; border:1px solid #d1d5db; border-radius:8px; font-size:14px; background:#fff; }
.filter-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:8px; }
.apply-btn { padding:10px 16px; background:var(--brand); color:#fff; border:none; border-radius:8px; font-size:14px; cursor:pointer; }
.apply-btn:hover { background:#1d4ed8; }
.reset-btn { padding:10px 16px; background:#fff; color:#1f2937; border:1px solid #d1d5db; border-radius:8px; font-size:14px; cursor:pointer; }
.reset-btn:hover { background:#f1f5f9; }
.store-content { min-width:0; }
/* Remove floating panel styles */
.filter-panel { display:none; }
.filter-btn { display:none; }
@media (max-width: 900px){ .store-layout { grid-template-columns: 1fr; } .filters-sidebar { position:relative; } }
/* AI Recommendation button */
.ai-reco-btn { padding:12px 18px; background:#0f766e; color:#fff; border:none; border-radius:10px; font-size:14px; font-weight:600; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,.08); }
.ai-reco-btn:hover { background:#0d5f59; }
/* AI Recommendation modal */
.ai-modal { border-radius:16px; }
.reco-layout { display:grid; grid-template-columns: 1fr 380px; gap:24px; }
@media (max-width: 1100px){ .reco-layout { grid-template-columns: 1fr; } .courses-column { order:2; } }
.chat-column { display:flex; flex-direction:column; }
.courses-column { background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:16px 16px 18px; display:flex; flex-direction:column; }
.panel-header h6 { margin:0 0 4px; font-size:16px; font-weight:600; }
.panel-header small { font-size:12px; color:#64748b; }
.panel-loading { padding:30px 0; text-align:center; font-size:14px; color:#2563eb; }
.reco-courses-list { display:flex; flex-direction:column; gap:14px; overflow-y:auto; max-height:360px; padding-right:4px; }
.reco-courses-list::-webkit-scrollbar { width:8px; }
.reco-courses-list::-webkit-scrollbar-track { background:transparent; }
.reco-courses-list::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:20px; }
.refine-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
.btn-refine { background:#0f766e; color:#fff; border:none; border-radius:8px; padding:8px 12px; font-size:12px; font-weight:600; cursor:pointer; }
.btn-refine:hover { background:#0d5f59; }
.msg { display:flex; }
.msg.system .bubble { background:#eef2ff; color:#1e3a8a; }
.msg.user { justify-content:flex-end; }
.msg.user .bubble { background:#2563eb; color:#fff; }
.msg.assistant .bubble { background:#f1f5f9; color:#1f2937; }
.bubble { padding:10px 14px; border-radius:14px; max-width:70%; font-size:13px; line-height:1.4; box-shadow:0 1px 3px rgba(0,0,0,.08); }
.chat-input-row { display:flex; gap:10px; margin-top:16px; }
.chat-input { flex:1; padding:12px 14px; border:1px solid #d1d5db; border-radius:12px; font-size:14px; }
.chat-input:focus { outline:none; border-color:#2563eb; box-shadow:0 0 0 3px rgba(37,99,235,.15); }
.send-btn { padding:12px 20px; background:#2563eb; color:#fff; border:none; border-radius:12px; font-weight:600; cursor:pointer; }
.send-btn:hover { background:#1d4ed8; }
.reco-courses { display:grid; gap:14px; margin-top:10px; }
.r-course { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,.05); }
.r-course.semantic { border-color:#6366f1; box-shadow:0 0 0 1px #6366f1 inset; }
.semantic-badge { display:inline-block; background:#6366f1; color:#fff; font-size:10px; font-weight:600; padding:3px 6px; border-radius:6px; margin-left:6px; letter-spacing:.5px; }
.r-course h6 { margin:0 0 4px; font-size:15px; font-weight:600; }
.r-desc { margin:0 0 6px; font-size:12px; color:#555; }
.r-tags { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:6px; }
.tag { font-size:10px; padding:4px 8px; border-radius:6px; background:#f1f5f9; color:#334155; font-weight:600; letter-spacing:.3px; }
.tag.cat { background:#dbeafe; color:#1e3a8a; }
.tag.topic { background:#fef3c7; color:#92400e; }
.r-meta { display:flex; gap:10px; font-size:11px; font-weight:600; margin-bottom:8px; }
.mini-enroll { padding:8px 12px; background:#2563eb; color:#fff; border:none; border-radius:8px; font-size:12px; cursor:pointer; }
.mini-enroll:hover { background:#1d4ed8; }
.mini-enroll.enrolled { background:#16a34a; }
.followup-row { margin-top:10px; display:flex; align-items:center; gap:10px; }
.followup-label { font-size:12px; font-weight:600; color:#555; }
.followup-btn { background:#6366f1; color:#fff; border:none; border-radius:8px; padding:6px 12px; font-size:12px; cursor:pointer; }
.followup-btn:hover { background:#4f46e5; }
.reason { font-size:11px; color:#334155; background:#f1f5f9; padding:6px 8px; border-radius:6px; margin:0 0 8px; }
.chat-window{ max-height: 360px; overflow-y:auto; padding-right:6px; }
.chat-window::-webkit-scrollbar{ width:8px; }
.chat-window::-webkit-scrollbar-thumb{ background:#cbd5e1; border-radius:20px; }
.chat-window::-webkit-scrollbar-track{ background:transparent; }
.pagination { margin:28px 0 0; display:flex; flex-wrap:wrap; gap:6px; align-items:center; }
.page-btn { min-width:42px; padding:8px 10px; border:1px solid #d1d5db; background:#fff; border-radius:8px; font-size:13px; cursor:pointer; transition:.15s; }
.page-btn:hover:not(:disabled){ background:#f1f5f9; }
.page-btn.active { background:#1d4ed8; color:#fff; border-color:#1d4ed8; font-weight:600; }
.page-btn:disabled { opacity:.5; cursor:not-allowed; }
.page-ellipsis { min-width:42px; display:inline-flex; justify-content:center; align-items:center; font-size:13px; color:#555; }
</style>
