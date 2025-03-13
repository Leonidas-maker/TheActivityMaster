import SessionPageGlobal from "@/src/globalPages/club/SessionPageGlobal";
import { useLocalSearchParams } from "expo-router";

const SessionPage = () => {
    const { club_id, program_id, session_id } = useLocalSearchParams();

    return <SessionPageGlobal club_id={club_id} program_id={program_id} session_id={session_id} route_name="search" />;
};

export default SessionPage;