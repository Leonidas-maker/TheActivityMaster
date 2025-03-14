import EventPageGlobal from "@/src/globalPages/club/EventPageGlobal";
import { useLocalSearchParams } from "expo-router";

const EventPage = () => {
    const { club_id, program_id, session_id, pricing_model } = useLocalSearchParams();

    return <EventPageGlobal club_id={club_id} program_id={program_id} session_id={session_id} pricing_model={pricing_model} route_name="(discover)" />;
};

export default EventPage;