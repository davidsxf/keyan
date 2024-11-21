function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("collapsed"); // 切换收缩类
}

// JavaScript 代码用于切换菜单的显示状态
document.addEventListener("DOMContentLoaded", () => {
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  if ($navbarBurgers.length > 0) {
    $navbarBurgers.forEach((el) => {
      el.addEventListener("click", () => {
        const target = el.dataset.target;
        const $target = document.getElementById(target);

        el.classList.toggle("is-active");
        $target.classList.toggle("is-active");
      });
    });
  }
});

function toggleSubmenu(event) {
  event.preventDefault(); // 防止链接跳转
  const submenu = event.target.nextElementSibling; // 获取下一个兄弟元素（子菜单）
  if (submenu.style.display === "block") {
    submenu.style.display = "none"; // 隐藏子菜单
  } else {
    submenu.style.display = "block"; // 显示子菜单
  }
}
