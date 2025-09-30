<template>
  <div 
    :class="['avatar-placeholder', sizeClass]"
    :style="{ backgroundColor: avatarColor }"
  >
    <span :class="['avatar-text', textSizeClass]">
      {{ initials }}
    </span>
  </div>
</template>

<script>
export default {
  name: 'UserAvatar',
  props: {
    name: {
      type: String,
      required: true
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large
      validator: value => ['small', 'medium', 'large'].includes(value)
    }
  },
  computed: {
    initials() {
      const names = this.name.split(' ');
      if (names.length >= 2) {
        return (names[0][0] + names[names.length - 1][0]).toUpperCase();
      }
      return this.name.substring(0, 2).toUpperCase();
    },
    
    avatarColor() {
      // Generate consistent color based on name
      let hash = 0;
      for (let i = 0; i < this.name.length; i++) {
        hash = this.name.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      const colors = [
        '#667eea', '#764ba2', '#f093fb', '#f5576c',
        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
        '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3',
        '#fad0c4', '#ffd1ff', '#8fd3f4', '#96e6a1'
      ];
      
      return colors[Math.abs(hash) % colors.length];
    },
    
    sizeClass() {
      return `avatar-${this.size}`;
    },
    
    textSizeClass() {
      return `text-${this.size}`;
    }
  }
}
</script>

<style scoped>
.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-small {
  width: 32px;
  height: 32px;
}

.avatar-medium {
  width: 40px;
  height: 40px;
}

.avatar-large {
  width: 56px;
  height: 56px;
}

.text-small {
  font-size: 0.75rem;
}

.text-medium {
  font-size: 0.875rem;
}

.text-large {
  font-size: 1.125rem;
}
</style>
