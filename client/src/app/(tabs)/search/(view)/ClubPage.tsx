import ClubPageGlobal from "@/src/globalPages/club/ClubPageGlobal";
import { useLocalSearchParams } from "expo-router";

const ClubPage = () => {
    const { club_id } = useLocalSearchParams();

    return <ClubPageGlobal club_id={club_id} route_name="search" />;
};

export default ClubPage;