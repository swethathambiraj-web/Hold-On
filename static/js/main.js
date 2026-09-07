/**
 * Hold On - Main JavaScript Controller
 */

// CSRF Token Helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Theme Switcher
function initTheme() {
  const savedTheme = localStorage.getItem('holdon-theme') || 'dark';
  document.documentElement.setAttribute('data-bs-theme', savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-bs-theme', newTheme);
  localStorage.setItem('holdon-theme', newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  const icons = document.querySelectorAll('.theme-toggle-icon');
  icons.forEach(icon => {
    if (theme === 'light') {
      icon.className = 'bi bi-moon-fill theme-toggle-icon';
    } else {
      icon.className = 'bi bi-sun-fill theme-toggle-icon';
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initTheme();

  // ==========================================================================
  // 1. Like / Unlike AJAX Handling
  // ==========================================================================
  document.addEventListener('click', async (e) => {
    const likeBtn = e.target.closest('.btn-like');
    if (!likeBtn) return;

    e.preventDefault();
    const postId = likeBtn.dataset.postId;
    if (!postId) return;

    try {
      const response = await fetch(`/posts/${postId}/like/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      const data = await response.json();

      const icon = likeBtn.querySelector('i');
      const countEl = document.querySelector(`.likes-count[data-post-id="${postId}"] span`);

      if (data.is_liked) {
        likeBtn.classList.add('liked');
        icon.className = 'bi bi-heart-fill';
      } else {
        likeBtn.classList.remove('liked');
        icon.className = 'bi bi-heart';
      }

      if (countEl) {
        countEl.textContent = data.likes_count;
      }
    } catch (err) {
      console.error('Like action failed:', err);
    }
  });

  // Double tap / double click to like on media
  document.addEventListener('dblclick', async (e) => {
    const mediaWrapper = e.target.closest('.post-media-wrapper');
    if (!mediaWrapper) return;

    const postId = mediaWrapper.dataset.postId;
    if (!postId) return;

    const burst = mediaWrapper.querySelector('.heart-burst');
    if (burst) {
      burst.classList.add('animate');
      setTimeout(() => burst.classList.remove('animate'), 600);
    }

    const likeBtn = document.querySelector(`.btn-like[data-post-id="${postId}"]`);
    if (likeBtn && !likeBtn.classList.contains('liked')) {
      likeBtn.click();
    }
  });

  // ==========================================================================
  // 2. Save / Bookmark AJAX Handling
  // ==========================================================================
  document.addEventListener('click', async (e) => {
    const saveBtn = e.target.closest('.btn-save');
    if (!saveBtn) return;

    e.preventDefault();
    const postId = saveBtn.dataset.postId;
    if (!postId) return;

    try {
      const response = await fetch(`/posts/${postId}/save/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      const data = await response.json();

      const icon = saveBtn.querySelector('i');
      if (data.is_saved) {
        saveBtn.classList.add('saved');
        icon.className = 'bi bi-bookmark-fill';
      } else {
        saveBtn.classList.remove('saved');
        icon.className = 'bi bi-bookmark';
      }
    } catch (err) {
      console.error('Save action failed:', err);
    }
  });

  // ==========================================================================
  // 3. Follow / Unfollow AJAX Handling
  // ==========================================================================
  document.addEventListener('click', async (e) => {
    const followBtn = e.target.closest('.btn-follow-toggle');
    if (!followBtn) return;

    e.preventDefault();
    const username = followBtn.dataset.username;
    if (!username) return;

    try {
      const response = await fetch(`/accounts/follow/${username}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      const data = await response.json();

      if (data.status === 'following') {
        followBtn.textContent = 'Following';
        followBtn.className = 'btn btn-surface btn-sm btn-follow-toggle';
      } else if (data.status === 'pending') {
        followBtn.textContent = 'Requested';
        followBtn.className = 'btn btn-surface btn-sm btn-follow-toggle';
      } else {
        followBtn.textContent = 'Follow';
        followBtn.className = 'btn btn-brand btn-sm btn-follow-toggle';
      }

      // Update followers count badge on profile if present
      const followersCountEl = document.querySelector('.followers-stat-num');
      if (followersCountEl && data.followers_count !== undefined) {
        followersCountEl.textContent = data.followers_count;
      }
    } catch (err) {
      console.error('Follow action failed:', err);
    }
  });

  // ==========================================================================
  // 4. Follow Request Accept / Deny Handling
  // ==========================================================================
  document.addEventListener('click', async (e) => {
    const reqBtn = e.target.closest('.btn-req-action');
    if (!reqBtn) return;

    const followId = reqBtn.dataset.followId;
    const action = reqBtn.dataset.action; // accept or deny
    const row = document.querySelector(`.req-row-${followId}`);

    try {
      const response = await fetch(`/accounts/follow-request/${followId}/${action}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      const data = await response.json();
      if (row) {
        row.remove();
      }
    } catch (err) {
      console.error('Follow request action failed:', err);
    }
  });

  // ==========================================================================
  // 5. Comments AJAX Submission & Deletion
  // ==========================================================================
  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('.comment-ajax-form');
    if (!form) return;

    e.preventDefault();
    const postId = form.dataset.postId;
    const input = form.querySelector('.comment-input');
    const text = input.value.trim();
    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);

    try {
      const response = await fetch(`/posts/${postId}/comment/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });
      const data = await response.json();

      if (response.ok) {
        input.value = '';
        const commentsList = document.querySelector(`.comments-list-${postId}`);
        if (commentsList) {
          const newCommentHtml = `
            <div class="comment-item mb-2" id="comment-${data.id}">
              <div class="d-flex align-items-start gap-2">
                <img src="${data.user.avatar_url}" class="author-avatar" style="width: 28px; height: 28px;" alt="${data.user.username}">
                <div class="flex-grow-1">
                  <span class="caption-username">${data.user.username}</span>
                  <span class="comment-text">${data.text}</span>
                  <div class="d-flex gap-3 mt-1">
                    <small class="text-muted" style="font-size: 0.72rem;">${data.created_at}</small>
                  </div>
                </div>
              </div>
            </div>
          `;
          commentsList.insertAdjacentHTML('afterbegin', newCommentHtml);
        }

        // Update comment counter in feed if exists
        const countLink = document.querySelector(`.view-comments-btn[data-post-id="${postId}"]`);
        if (countLink) {
          countLink.textContent = `View all ${data.comments_count} comments`;
        }
      }
    } catch (err) {
      console.error('Failed to post comment:', err);
    }
  });

  // Delete comment
  document.addEventListener('click', async (e) => {
    const delBtn = e.target.closest('.btn-delete-comment');
    if (!delBtn) return;

    e.preventDefault();
    const commentId = delBtn.dataset.commentId;
    if (!confirm('Delete this comment?')) return;

    try {
      const response = await fetch(`/posts/comment/${commentId}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      if (response.ok) {
        const commentEl = document.getElementById(`comment-${commentId}`);
        if (commentEl) commentEl.remove();
      }
    } catch (err) {
      console.error('Failed to delete comment:', err);
    }
  });

  // ==========================================================================
  // 6. Live Search Autocomplete (Debounced)
  // ==========================================================================
  const searchInput = document.querySelector('#global-search-input');
  const searchDropdown = document.querySelector('#search-results-dropdown');

  if (searchInput && searchDropdown) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const q = searchInput.value.trim();

      if (q.length < 2) {
        searchDropdown.style.display = 'none';
        searchDropdown.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/search/?q=${encodeURIComponent(q)}&format=json`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          });
          const data = await res.json();

          let html = '';
          if (data.users && data.users.length > 0) {
            html += '<div class="p-2 text-muted fw-bold" style="font-size:0.75rem;">USERS</div>';
            data.users.forEach(u => {
              html += `
                <a href="/accounts/profile/${u.username}/" class="d-flex align-items-center gap-3 p-2 text-decoration-none dropdown-user-item">
                  <img src="${u.avatar_url}" class="rounded-circle" style="width:36px; height:36px; object-fit:cover;" alt="${u.username}">
                  <div>
                    <div class="fw-bold text-light" style="font-size:0.88rem;">${u.username}</div>
                    <div class="text-muted" style="font-size:0.78rem;">${u.name}</div>
                  </div>
                </a>
              `;
            });
          }

          if (data.hashtags && data.hashtags.length > 0) {
            html += '<div class="p-2 text-muted fw-bold border-top mt-1" style="font-size:0.75rem;">HASHTAGS</div>';
            data.hashtags.forEach(h => {
              html += `
                <a href="/posts/tags/${h.name}/" class="d-flex align-items-center gap-3 p-2 text-decoration-none dropdown-user-item">
                  <div class="d-flex align-items-center justify-content-center rounded-circle bg-surface" style="width:36px; height:36px;">
                    <i class="bi bi-hash fs-5 text-primary"></i>
                  </div>
                  <div>
                    <div class="fw-bold text-light" style="font-size:0.88rem;">#${h.name}</div>
                    <div class="text-muted" style="font-size:0.78rem;">${h.posts_count} posts</div>
                  </div>
                </a>
              `;
            });
          }

          if (!html) {
            html = '<div class="p-3 text-muted text-center" style="font-size:0.85rem;">No results found</div>';
          }

          searchDropdown.innerHTML = html;
          searchDropdown.style.display = 'block';
        } catch (err) {
          console.error('Search query failed:', err);
        }
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }
});

// ==========================================================================
// 7. Story Viewer Modal Controller
// ==========================================================================
const StoryViewer = {
  currentStories: [],
  currentIndex: 0,
  timer: null,
  duration: 5000,
  startTime: 0,

  async openUserStories(username) {
    try {
      const res = await fetch(`/stories/user/${username}/json/`);
      if (!res.ok) return;
      const data = await res.json();

      if (!data.stories || data.stories.length === 0) return;

      this.currentStories = data.stories;
      this.userData = data.user;
      this.currentIndex = 0;

      const backdrop = document.getElementById('story-viewer-modal');
      if (!backdrop) return;

      backdrop.style.display = 'flex';
      this.renderStory();
    } catch (err) {
      console.error('Failed to load story:', err);
    }
  },

  renderStory() {
    clearTimeout(this.timer);

    const story = this.currentStories[this.currentIndex];
    if (!story) {
      this.close();
      return;
    }

    // Mark as viewed in backend
    fetch(`/stories/${story.id}/view/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
      }
    });

    // Update UI elements
    const avatar = document.getElementById('story-modal-user-avatar');
    const username = document.getElementById('story-modal-username');
    const time = document.getElementById('story-modal-time');
    const media = document.getElementById('story-modal-media');
    const caption = document.getElementById('story-modal-caption');

    if (avatar) avatar.src = this.userData.avatar_url;
    if (username) username.textContent = this.userData.username;
    if (time) time.textContent = story.created_at;
    if (media) media.src = story.media_url;

    if (caption) {
      if (story.caption) {
        caption.textContent = story.caption;
        caption.style.display = 'block';
      } else {
        caption.style.display = 'none';
      }
    }

    // Render Progress Segments
    const progressContainer = document.getElementById('story-progress-bars');
    if (progressContainer) {
      progressContainer.innerHTML = '';
      this.currentStories.forEach((_, idx) => {
        const seg = document.createElement('div');
        seg.className = 'story-progress-seg';
        const fill = document.createElement('div');
        fill.className = 'story-progress-fill';
        if (idx < this.currentIndex) {
          fill.style.width = '100%';
        } else if (idx === this.currentIndex) {
          fill.style.width = '0%';
          fill.style.transition = `width ${this.duration}ms linear`;
          setTimeout(() => fill.style.width = '100%', 20);
        } else {
          fill.style.width = '0%';
        }
        seg.appendChild(fill);
        progressContainer.appendChild(seg);
      });
    }

    this.timer = setTimeout(() => {
      this.next();
    }, this.duration);
  },

  next() {
    if (this.currentIndex < this.currentStories.length - 1) {
      this.currentIndex++;
      this.renderStory();
    } else {
      this.close();
    }
  },

  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.renderStory();
    }
  },

  close() {
    clearTimeout(this.timer);
    const backdrop = document.getElementById('story-viewer-modal');
    if (backdrop) backdrop.style.display = 'none';
  }
};
