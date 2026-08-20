/*
 * Movie Watchlist - Client-side Interactions
 *
 * ไฟล์นี้จัดการ interaction ฝั่ง browser
 * ที่ไม่จำเป็นต้องเปลี่ยน Django backend logic
 *
 * หน้าที่หลักมีสองส่วน:
 *
 * 1. Show More / Show Less
 *    - แสดง Movie เริ่มต้นสูงสุด 8 cards ต่อ section
 *    - ถ้ามีมากกว่า 8 จึงเปิด Show More
 *    - PLAN TO WATCH และ WATCHED ถูกจัดการแยกกัน
 *
 * 2. Preserve Rating Scroll Position
 *    - Rating ยังคง submit ด้วย POST Form ปกติ
 *    - Django movie_rate() ยังคง validation และ save PostgreSQL
 *    - ก่อน submit จะจำตำแหน่ง scroll ปัจจุบัน
 *    - หลัง Django redirect กลับ Home
 *      browser จะเลื่อนกลับมายังตำแหน่งเดิม
 *
 * JavaScript ไม่ได้แทนที่ Django backend
 * และไม่ได้เขียนข้อมูล Movie ลง PostgreSQL โดยตรง
 */


// บอก browser ว่าการคืนตำแหน่ง scroll
// หลัง navigation/reload จะถูกจัดการโดย JavaScript เอง
//
// ช่วยลดกรณีที่ browser พยายามคืนตำแหน่งอัตโนมัติ
// พร้อมกับ code ของเราและเกิดการกระโดดสองครั้ง
if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
}


// DOMContentLoaded ทำให้ code เริ่มทำงาน
// หลัง browser สร้าง HTML structure เสร็จแล้ว
//
// ตอนนี้ querySelector สามารถหา:
// - Movie Sections
// - Movie Cards
// - Show More buttons
// - Rating Forms
//
// ได้อย่างปลอดภัย
document.addEventListener("DOMContentLoaded", () => {

    /*
     * 1. Shared Configuration
     *
     * จำนวน Movie ที่ต้องการแสดงเริ่มต้น
     * ในแต่ละ section
     */
    const initialVisibleCount = 8;


    /*
     * sessionStorage ใช้เก็บข้อมูลชั่วคราว
     * เฉพาะ browser tab ปัจจุบัน
     *
     * ข้อมูลเหล่านี้:
     * - ไม่ถูกส่งไป Django
     * - ไม่ถูกบันทึกใน PostgreSQL
     * - ไม่ใช่ secret
     *
     * ratingScrollKey:
     *     เก็บตำแหน่ง scroll ก่อนกด Rating
     *
     * expandedSectionsKey:
     *     เก็บว่า section ไหนกำลัง Show More อยู่
     */
    const ratingScrollKey =
        "movieWatchlistRatingScrollPosition";

    const expandedSectionsKey =
        "movieWatchlistExpandedSections";



    /*
     * 2. Show More / Show Less
     *
     * หา section ทั้งหมดที่มี:
     *
     * data-movie-section
     *
     * ใน movie_list.html ปัจจุบันมี:
     *
     * section index 0
     * → PLAN TO WATCH
     *
     * section index 1
     * → WATCHED
     */
    const movieSections = Array.from(
        document.querySelectorAll(
            "[data-movie-section]"
        )
    );


    /*
     * อ่านสถานะ section ที่เคยเปิด Show More
     *
     * ตัวอย่าง:
     *
     * [0]
     *
     * หมายถึง PLAN TO WATCH เปิดอยู่
     *
     * [1]
     *
     * หมายถึง WATCHED เปิดอยู่
     *
     * [0, 1]
     *
     * หมายถึงทั้งสอง section เปิดอยู่
     */
    let expandedSectionIndexes = [];


    try {
        const storedExpandedSections =
            sessionStorage.getItem(
                expandedSectionsKey
            );

        if (storedExpandedSections) {

            const parsedSections =
                JSON.parse(
                    storedExpandedSections
                );


            // Defensive check
            //
            // รับเฉพาะข้อมูลที่เป็น Array
            // เพื่อป้องกัน JavaScript error
            // หาก sessionStorage มีข้อมูลผิดรูปแบบ
            if (Array.isArray(parsedSections)) {
                expandedSectionIndexes =
                    parsedSections;
            }
        }

    } catch (error) {

        // ถ้าข้อมูลใน sessionStorage ผิดรูปแบบ
        // ให้เริ่มต้นเหมือนไม่มี section ไหน expanded
        //
        // ไม่จำเป็นต้องหยุด JavaScript ทั้งไฟล์
        expandedSectionIndexes = [];
    }



    /*
     * จัดการแต่ละ Movie Section แยกกัน
     *
     * sectionIndex ใช้เป็น ID ชั่วคราว
     * สำหรับจำสถานะ Show More
     */
    movieSections.forEach(
        (section, sectionIndex) => {

            // หา Movie Cards เฉพาะใน section ปัจจุบัน
            //
            // Array.from() ทำให้ใช้:
            // slice()
            // forEach()
            //
            // ได้สะดวก
            const cards = Array.from(
                section.querySelectorAll(
                    "[data-movie-card]"
                )
            );


            // หา Show More / Show Less button
            // ภายใน section ปัจจุบัน
            const toggleButton =
                section.querySelector(
                    "[data-show-more]"
                );


            /*
             * ถ้ามี Movie ไม่เกิน 8 เรื่อง
             * ไม่จำเป็นต้องมี Show More
             *
             * ถ้าไม่มี toggleButton
             * ก็หยุดจัดการ section นี้
             * เพื่อป้องกัน null error
             */
            if (
                cards.length <= initialVisibleCount
                || !toggleButton
            ) {
                return;
            }


            /*
             * ตรวจว่า section นี้เคยเปิด
             * Show More ก่อน page reload หรือไม่
             */
            const shouldStartExpanded =
                expandedSectionIndexes.includes(
                    sectionIndex
                );


            if (shouldStartExpanded) {

                /*
                 * Restore Expanded State
                 *
                 * Movie ทุกใบต้องแสดง
                 */
                cards.forEach((card) => {

                    card.classList.remove(
                        "movie-card-hidden"
                    );
                });


                toggleButton.textContent =
                    "Show Less";

                toggleButton.setAttribute(
                    "aria-expanded",
                    "true"
                );

            } else {

                /*
                 * Default Collapsed State
                 *
                 * แสดงเพียง 8 Movie แรก
                 */
                cards
                    .slice(initialVisibleCount)
                    .forEach((card) => {

                        card.classList.add(
                            "movie-card-hidden"
                        );
                    });


                toggleButton.textContent =
                    "Show More";

                toggleButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }


            // section มี Movie มากกว่า 8 แน่นอนแล้ว
            // จึงเปิด button ให้เห็น
            toggleButton.hidden = false;



            /*
             * เมื่อกด Show More / Show Less
             */
            toggleButton.addEventListener(
                "click",
                () => {

                    const isExpanded =
                        toggleButton.getAttribute(
                            "aria-expanded"
                        ) === "true";


                    if (isExpanded) {

                        /*
                         * Show Less
                         *
                         * ซ่อน Movie หลังลำดับที่ 8
                         */
                        cards
                            .slice(initialVisibleCount)
                            .forEach((card) => {

                                card.classList.add(
                                    "movie-card-hidden"
                                );
                            });


                        toggleButton.textContent =
                            "Show More";

                        toggleButton.setAttribute(
                            "aria-expanded",
                            "false"
                        );


                        /*
                         * ลบ section ปัจจุบันออกจาก
                         * expandedSectionIndexes
                         */
                        expandedSectionIndexes =
                            expandedSectionIndexes.filter(
                                (storedIndex) =>
                                    storedIndex
                                    !== sectionIndex
                            );


                        /*
                         * หลัง Show Less
                         * ความสูงของหน้าอาจลดลงมาก
                         *
                         * จึงเลื่อนกลับมายังหัว section
                         * เพื่อไม่ให้ viewport อยู่ในพื้นที่
                         * ที่เพิ่งถูกซ่อน
                         */
                        section.scrollIntoView({
                            behavior: "smooth",
                            block: "start",
                        });

                    } else {

                        /*
                         * Show More
                         *
                         * เปิด Movie Cards ทั้งหมด
                         */
                        cards.forEach((card) => {

                            card.classList.remove(
                                "movie-card-hidden"
                            );
                        });


                        toggleButton.textContent =
                            "Show Less";

                        toggleButton.setAttribute(
                            "aria-expanded",
                            "true"
                        );


                        /*
                         * เพิ่ม section ปัจจุบันเข้า Array
                         * ถ้ายังไม่มีอยู่
                         */
                        if (
                            !expandedSectionIndexes.includes(
                                sectionIndex
                            )
                        ) {
                            expandedSectionIndexes.push(
                                sectionIndex
                            );
                        }
                    }


                    /*
                     * บันทึก Show More state
                     *
                     * ตัวอย่าง:
                     *
                     * [1]
                     *
                     * หมายถึง WATCHED section
                     * ยังคงเปิดอยู่หลังหน้า reload
                     */
                    sessionStorage.setItem(
                        expandedSectionsKey,
                        JSON.stringify(
                            expandedSectionIndexes
                        )
                    );
                }
            );
        }
    );



    /*
     * 3. Preserve Scroll Position for Rating
     *
     * Rating Form ยังคงเป็น HTML POST Form ปกติ
     *
     * ไม่มี:
     * event.preventDefault()
     * fetch()
     *
     * ดังนั้น Django flow เดิมยังทำงาน:
     *
     * Browser
     *     ↓
     * POST
     *     ↓
     * movie_rate()
     *     ↓
     * Validate
     *     ↓
     * Save PostgreSQL
     *     ↓
     * redirect("movie_list")
     *
     * JavaScript มีหน้าที่เพียงจำว่า
     * ก่อน POST ผู้ใช้อยู่ตรงไหนของหน้า
     */


    // หา Rating Forms ทั้งหมด
    //
    // movie_list.html ต้องมี:
    //
    // data-rating-form
    const ratingForms =
        document.querySelectorAll(
            "[data-rating-form]"
        );


    ratingForms.forEach((form) => {

        /*
         * Event นี้ทำงานก่อน Form ถูกส่งไป Django
         *
         * จงใจไม่ใช้ preventDefault()
         * เพราะต้องการให้ Form submit ตามปกติ
         */
        form.addEventListener(
            "submit",
            () => {

                /*
                 * window.scrollY คือระยะจาก
                 * ด้านบนของหน้าเป็น pixel
                 *
                 * ตัวอย่าง:
                 *
                 * 0
                 * → อยู่บนสุด
                 *
                 * 1800
                 * → เลื่อนลงมาประมาณ 1800px
                 */
                sessionStorage.setItem(
                    ratingScrollKey,
                    String(window.scrollY)
                );


                /*
                 * เก็บสถานะ Show More ล่าสุด
                 * อีกครั้งก่อน submit
                 *
                 * สำคัญกรณีผู้ใช้ให้คะแนน Movie
                 * ที่อยู่หลังลำดับที่ 8
                 */
                sessionStorage.setItem(
                    expandedSectionsKey,
                    JSON.stringify(
                        expandedSectionIndexes
                    )
                );


                /*
                 * หลังจาก event นี้จบ
                 * Browser จะ submit Form ตามปกติ
                 *
                 * ไม่มี return false
                 * ไม่มี preventDefault()
                 * ไม่มี fetch()
                 */
            }
        );
    });



    /*
     * 4. Restore Rating Scroll Position
     *
     * หลัง Django redirect กลับ Home
     * DOMContentLoaded จะทำงานใหม่
     *
     * ถ้าพบตำแหน่งที่บันทึกไว้
     * แปลว่าหน้านี้เพิ่งกลับมาจาก Rating POST
     */
    const savedRatingScroll =
        sessionStorage.getItem(
            ratingScrollKey
        );


    if (savedRatingScroll !== null) {

        const scrollPosition =
            Number(savedRatingScroll);


        if (
            Number.isFinite(
                scrollPosition
            )
        ) {

            /*
             * ฟังก์ชันเล็กสำหรับคืนตำแหน่ง
             *
             * ใช้ scrollTo แบบทันที
             * เพราะไม่ต้องการให้ผู้ใช้เห็น animation
             * วิ่งจากด้านบนกลับลงมาหลัง Rating
             */
            const restoreScrollPosition = () => {

                window.scrollTo({
                    top: scrollPosition,
                    left: 0,
                    behavior: "auto",
                });
            };


            /*
             * รอบแรก:
             *
             * รอ browser render DOM frame แรก
             *
             * ตอนนี้ Show More state
             * ถูก restore ด้านบนแล้วด้วย
             */
            requestAnimationFrame(() => {

                restoreScrollPosition();


                /*
                 * requestAnimationFrame รอบที่สอง
                 * ช่วยให้ layout เช่น CSS Grid
                 * มีโอกาสคำนวณขนาดเสร็จมากขึ้น
                 */
                requestAnimationFrame(() => {
                    restoreScrollPosition();
                });
            });


            /*
             * Poster ใช้ aspect-ratio อยู่แล้ว
             * จึงไม่ควรเปลี่ยน layout มาก
             *
             * แต่เพื่อความแม่นยำ
             * เมื่อ window โหลด resources ครบ
             * จะคืนตำแหน่งอีกครั้ง
             */
            window.addEventListener(
                "load",
                restoreScrollPosition,
                {
                    once: true,
                }
            );


            /*
             * Browser บางกรณีอาจมีการเปลี่ยน layout
             * หลัง font/image/static resources เริ่มทำงาน
             *
             * จึงมี final correction หลังจากช่วงสั้น ๆ
             */
            window.setTimeout(
                restoreScrollPosition,
                100
            );
        }


        /*
         * Scroll position ใช้เพียงครั้งเดียว
         *
         * ต้องลบหลังอ่าน
         * ไม่อย่างนั้นการ Refresh หน้าเองครั้งต่อไป
         * จะยังถูกบังคับกลับมาตำแหน่ง Rating เดิม
         */
        sessionStorage.removeItem(
            ratingScrollKey
        );
    }
});