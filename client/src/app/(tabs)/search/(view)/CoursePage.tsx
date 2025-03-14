import CoursePageGlobal from "@/src/globalPages/club/CoursePageGlobal";
import { useLocalSearchParams } from "expo-router";

const CoursePage = () => {
    const { club_id, program_id, session_id, pricing_model } = useLocalSearchParams();

    return <CoursePageGlobal club_id={club_id} program_id={program_id} session_id={session_id} pricing_model={pricing_model} route_name="search" />;
};

export default CoursePage;