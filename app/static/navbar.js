// Navbar 메뉴 생성 공통 함수
function initNavbar(userRole, currentPage) {
    const navbarMenu = document.getElementById("navbarMenu");
    const mobileMenuList = document.getElementById("mobileMenuList");
    const menuList = document.getElementById("menuList");
    const navbarToggle = document.getElementById("navbarToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    
    let menuItems = [];

    if (userRole === "student") {
        menuItems = [
            { name: "시간표", url: "/timetable" },
            { name: "출석체크", url: "/attendance" },
            { name: "출석관리", url: "/attendance/manage" },
            { name: "로그아웃", url: "/auth/logout" }
        ];
    } else if (userRole === "professor") {
        menuItems = [
            { name: "출석 관리", url: "/professor/lectures" },
            { name: "시간표", url: "/timetable" },
            { name: "로그아웃", url: "/auth/logout" }
        ];
    }

    // 현재 페이지 확인
    menuItems.forEach(item => {
        if (currentPage && item.name === currentPage) {
            item.current = true;
        }
    });

    // PC Navbar 메뉴 생성
    function createNavbarMenuItem(item) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        const isCurrent = item.current || false;
        
        if (isCurrent) {
            a.classList.add('active');
            a.href = '#';
            a.addEventListener('click', (e) => {
                e.preventDefault();
            });
        } else {
            a.href = item.url;
        }
        
        a.textContent = item.name;
        li.appendChild(a);
        return li;
    }

    // 모바일 사이드바 메뉴 생성
    function createMobileMenuItem(item) {
        const isCurrent = item.current || false;
        const li = renderMenuItem(item, isCurrent);
        const link = li.querySelector('a');

        if (isCurrent) {
            link.addEventListener('click', (e) => {
                e.preventDefault();
            });
        }

        return li;
    }

    // 메뉴 렌더링
    if (navbarMenu) {
        menuItems.forEach(item => {
            navbarMenu.appendChild(createNavbarMenuItem(item));
        });
    }
    
    if (mobileMenuList) {
        menuItems.forEach(item => {
            mobileMenuList.appendChild(createMobileMenuItem(item));
        });
    }
    
    if (menuList) {
        menuItems.forEach(item => {
            menuList.appendChild(createMobileMenuItem(item));
        });
    }

    // 모바일 메뉴 토글
    if (navbarToggle && mobileMenu) {
        navbarToggle.addEventListener('click', () => {
            navbarToggle.classList.toggle('active');
            mobileMenu.classList.toggle('active');
        });
    }
}

