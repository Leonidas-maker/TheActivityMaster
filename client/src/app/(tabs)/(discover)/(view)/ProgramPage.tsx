import ProgramPageGlobal from "@/src/globalPages/club/ProgramPageGlobal";
import { useLocalSearchParams } from "expo-router";

const ProgramPage = () => {
    const { club_id, program_id } = useLocalSearchParams();

    return <ProgramPageGlobal club_id={club_id} program_id={program_id} route_name="(discover)" />;
};

export default ProgramPage;