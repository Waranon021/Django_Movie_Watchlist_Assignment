/*
 * Movie Watchlist - Show More / Show Less
 *
 * หน้าที่ของไฟล์นี้:
 * - ตรวจ Movie cards ในแต่ละ section
 * - แสดงเริ่มต้นสูงสุด 8 cards
 * - ถ้ามีมากกว่า 8 จึงแสดง Show More
 * - Show More เปิด cards ที่เหลือ
 * - Show Less กลับมาแสดง 8 cards แรก
 *
 * JavaScript นี้เปลี่ยนเฉพาะสิ่งที่ผู้ใช้มองเห็น
 * ไม่ได้แก้ Movie object หรือข้อมูลใน PostgreSQL
 *
 * Movie ทั้งหมดถูก Django render ลง HTML ตั้งแต่แรก
 * ดังนั้น functionality หลักของ Assignment
 * ที่ต้องแสดง Movie ใน Watchlist ยังอยู่ครบ
 */


// DOMContentLoaded ทำให้ code เริ่มทำงาน
// หลัง browser อ่าน HTML structure เสร็จแล้ว
//
// ถ้ารัน JavaScript ก่อน HTML ถูกสร้าง
// querySelector อาจยังหา Movie sections ไม่เจอ
document.addEventListener("DOMContentLoaded", () => {

    // จำนวน Movie cards ที่ต้องการแสดง
    // ตอนเปิดหน้าเป็นครั้งแรก
    const initialVisibleCount = 8;


    // หา section ทั้งหมดที่มี attribute:
    // data-movie-section
    //
    // ใน movie_list.html มีสอง section:
    // - PLAN TO WATCH
    // - WATCHED
    //
    // การใช้ data attribute ทำให้ JavaScript
    // ไม่ต้องผูก logic กับชื่อ CSS class สำหรับ styling
    const movieSections = document.querySelectorAll(
        "[data-movie-section]"
    );


    // แต่ละ section ถูกจัดการแยกจากกัน
    //
    // ตัวอย่าง:
    // PLAN TO WATCH = 12 Movies
    // WATCHED       = 5 Movies
    //
    // จะมี Show More เฉพาะ PLAN TO WATCH
    movieSections.forEach((section) => {

        // หา Movie cards ภายใน section ปัจจุบันเท่านั้น
        //
        // Array.from() เปลี่ยน NodeList
        // ให้เป็น JavaScript Array
        // เพื่อใช้ methods เช่น slice() ได้สะดวก
        const cards = Array.from(
            section.querySelectorAll("[data-movie-card]")
        );


        // หา Show More button ของ section ปัจจุบัน
        const toggleButton = section.querySelector(
            "[data-show-more]"
        );


        // ถ้ามี Movie ไม่เกิน 8 เรื่อง
        // ไม่จำเป็นต้องซ่อน card หรือแสดง Show More
        //
        // !toggleButton เป็น defensive check
        // ถ้า HTML ไม่มี button ด้วยเหตุผลใดก็ตาม
        // JavaScript จะหยุดส่วนนี้แทนการเกิด error
        if (
            cards.length <= initialVisibleCount
            || !toggleButton
        ) {
            return;
        }


        // slice(8) หมายถึงเลือก cards
        // ตั้งแต่ index 8 เป็นต้นไป
        //
        // เนื่องจาก array เริ่ม index ที่ 0:
        // index 0–7 = 8 cards แรก
        //
        // card ที่เหลือจะถูกเพิ่ม CSS class
        // movie-card-hidden เพื่อซ่อนทาง presentation
        cards
            .slice(initialVisibleCount)
            .forEach((card) => {

                card.classList.add(
                    "movie-card-hidden"
                );

            });


        // ใน HTML button เริ่มต้นมี hidden
        //
        // เมื่อ JavaScript ยืนยันแล้วว่า
        // section มีมากกว่า 8 Movies
        // จึงเปิดให้ผู้ใช้เห็น button
        toggleButton.hidden = false;



        // เมื่อผู้ใช้กด Show More / Show Less
        // event listener นี้จะทำงาน
        toggleButton.addEventListener("click", () => {

            // aria-expanded เก็บสถานะว่า
            // section ปัจจุบันถูกเปิดทั้งหมดหรือยัง
            //
            // "true"  = กำลังแสดงทั้งหมด
            // "false" = กำลังแสดงเฉพาะ 8 เรื่องแรก
            const isExpanded =
                toggleButton.getAttribute(
                    "aria-expanded"
                ) === "true";


            if (isExpanded) {

                // ถ้าตอนนี้เปิดทั้งหมดอยู่
                // การกด button หมายถึง Show Less
                //
                // จึงซ่อน Movie หลังลำดับที่ 8 อีกครั้ง
                cards
                    .slice(initialVisibleCount)
                    .forEach((card) => {

                        card.classList.add(
                            "movie-card-hidden"
                        );

                    });


                // เปลี่ยนข้อความกลับเป็น Show More
                toggleButton.textContent = "Show More";


                // อัปเดต accessibility state
                toggleButton.setAttribute(
                    "aria-expanded",
                    "false"
                );


                // หลัง Show Less ความสูงของหน้า
                // อาจลดลงอย่างมาก
                //
                // จึงเลื่อนกลับไปยัง section ปัจจุบัน
                // เพื่อไม่ให้ตำแหน่ง viewport ดูเหมือนกระโดด
                section.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });

            } else {

                // ถ้ายังแสดงเพียง 8 Movies
                // การกด button หมายถึง Show More
                //
                // ลบ movie-card-hidden
                // ออกจากทุก Movie card ใน section
                cards.forEach((card) => {

                    card.classList.remove(
                        "movie-card-hidden"
                    );

                });


                // เปลี่ยนข้อความ button
                toggleButton.textContent = "Show Less";


                // แจ้ง accessibility state
                // ว่า content ถูก expand แล้ว
                toggleButton.setAttribute(
                    "aria-expanded",
                    "true"
                );
            }
        });
    });
});