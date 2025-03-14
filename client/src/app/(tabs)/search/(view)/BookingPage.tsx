import BookingPageGlobal from "@/src/globalPages/club/BookingPageGlobal";
import { useLocalSearchParams } from "expo-router";

const BookingPage = () => {
    // Get the search parameters from the URL
    const params = useLocalSearchParams();

    // Extract the required club_id
    const club_id = params.club_id;

    // Build an object for optional props only if they are defined
    const optionalProps: { [key: string]: any } = {};

    // If program_id is set, include it
    if ('program_id' in params) {
        optionalProps.program_id = params.program_id;
    }

    // If session_id is set, include it
    if ('session_id' in params) {
        optionalProps.session_id = params.session_id;
    }

    // If is_membership is set, convert it to boolean and include it
    if ('is_membership' in params) {
        optionalProps.is_membership = params.is_membership === 'true';
    }

    // If membership_id is set, include it
    if ('membership_id' in params) {
        optionalProps.membership_id = params.membership_id;
    }

    // If price is set, convert it to a number and include it
    if ('price' in params) {
        optionalProps.price = Number(params.price);
    }

    // If name is set, ensure it is a string and include it
    if ('name' in params) {
        optionalProps.name = String(params.name);
    }

    return (
        <BookingPageGlobal 
            club_id={club_id}
            route_name="search"
            {...optionalProps}
        />
    );
};

export default BookingPage;