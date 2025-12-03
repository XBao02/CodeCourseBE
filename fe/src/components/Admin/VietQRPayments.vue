<template>
  <div class="payments-wrapper">
    <div class="header-row">
      <div>
        <h3>VietQR Payments</h3>
        <p class="muted">Duyệt thanh toán chuyển khoản thủ công</p>
      </div>
      <div class="actions">
        <button class="btn" @click="loadInvoices" :disabled="loading">Làm mới</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Đang tải...</div>
    <div v-else-if="!invoices.length" class="empty">Không có hoá đơn chờ duyệt.</div>
    <div v-else class="table-wrapper">
      <table class="tbl">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Khoá học</th>
            <th>Học viên</th>
            <th>Số tiền</th>
            <th>Ghi chú chuyển khoản</th>
            <th>Trạng thái</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.invoiceNumber">
            <td>
              <div class="cell-title">{{ inv.invoiceNumber }}</div>
              <div class="cell-sub">Mã thanh toán: {{ inv.paymentMethod }}</div>
            </td>
            <td>
              <div class="cell-title">{{ inv.courseTitle || 'N/A' }}</div>
              <div class="cell-sub">Course ID: {{ inv.courseId }}</div>
            </td>
            <td>
              <div class="cell-title">{{ inv.studentName || 'N/A' }}</div>
              <div class="cell-sub">{{ inv.studentEmail }}</div>
            </td>
            <td>
              <div class="cell-title">{{ formatAmount(inv.amount, inv.currency) }}</div>
              <div class="cell-sub">Ref: {{ inv.referenceCode || 'N/A' }}</div>
            </td>
            <td>{{ inv.transfer_note || inv.referenceCode || 'N/A' }}</td>
            <td><span class="badge pending">{{ inv.paymentStatus }}</span></td>
            <td class="actions-cell">
              <button class="btn approve" @click="approve(inv.invoiceNumber)" :disabled="inv._busy">Duyệt</button>
              <button class="btn reject" @click="reject(inv.invoiceNumber)" :disabled="inv._busy">Từ chối</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService'

export default {
  name: 'VietQRPayments',
  data() {
    return {
      invoices: [],
      loading: false,
    }
  },
  mounted() {
    this.loadInvoices()
  },
  methods: {
    formatAmount(val, currency) {
      try {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: currency || 'VND' }).format(val || 0)
      } catch {
        return `${val || 0} ${currency || ''}`
      }
    },
    async loadInvoices() {
      this.loading = true
      try {
        const data = await adminService.getPendingInvoices()
        this.invoices = Array.isArray(data) ? data.map(d => ({ ...d, _busy: false })) : []
      } catch (e) {
        console.error('Load pending invoices failed', e)
        alert('Không tải được danh sách hoá đơn.')
      } finally {
        this.loading = false
      }
    },
    async approve(invoiceNumber) {
      const target = this.invoices.find(i => i.invoiceNumber === invoiceNumber)
      if (target) target._busy = true
      try {
        await adminService.approveInvoice(invoiceNumber)
        this.invoices = this.invoices.filter(i => i.invoiceNumber !== invoiceNumber)
      } catch (e) {
        console.error('Approve failed', e)
        alert('Không duyệt được hoá đơn.')
      } finally {
        if (target) target._busy = false
      }
    },
    async reject(invoiceNumber) {
      const target = this.invoices.find(i => i.invoiceNumber === invoiceNumber)
      if (target) target._busy = true
      try {
        await adminService.rejectInvoice(invoiceNumber)
        this.invoices = this.invoices.filter(i => i.invoiceNumber !== invoiceNumber)
      } catch (e) {
        console.error('Reject failed', e)
        alert('Không từ chối được hoá đơn.')
      } finally {
        if (target) target._busy = false
      }
    },
  },
}
</script>

<style scoped>
.payments-wrapper {
  padding: 24px;
  background: #f7f8fa;
  min-height: 100vh;
}
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.muted { color: #6b7280; margin: 4px 0 0; }
.actions { display: flex; gap: 8px; }
.btn {
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn.approve { background: #16a34a; }
.btn.reject { background: #dc2626; }
.table-wrapper {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  overflow: hidden;
}
.tbl { width: 100%; border-collapse: collapse; }
.tbl th, .tbl td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; text-align: left; font-size: 14px; }
.tbl thead { background: #f8fafc; }
.cell-title { font-weight: 600; color: #111827; }
.cell-sub { color: #6b7280; font-size: 12px; }
.badge.pending { background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 8px; font-weight: 700; font-size: 12px; }
.actions-cell { display: flex; gap: 8px; }
.loading, .empty { padding: 16px; color: #6b7280; }
</style>
