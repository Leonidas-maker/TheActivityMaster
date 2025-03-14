import MembershipPageGlobal from "@/src/globalPages/club/MembershipPageGlobal";
import { useLocalSearchParams } from "expo-router";

const MembershipPage = () => {
    const { club_id, membership_id } = useLocalSearchParams();

    return <MembershipPageGlobal club_id={club_id} membership_id={membership_id} route_name="(discover)" />;
};

export default MembershipPage;