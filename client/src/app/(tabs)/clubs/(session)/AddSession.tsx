import DateTimePicker, { DateType, getDefaultStyles } from 'react-native-ui-datepicker';

let tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
const defaultStyles = getDefaultStyles();
const [startDate, setStartDate] = useState<DateType>();
const [endDate, setEndDate] = useState<DateType>();

<DateTimePicker
    mode="range"
    startDate={startDate}
    endDate={endDate}
    onChange={({ startDate, endDate }) => {
        setStartDate(startDate);
        setEndDate(endDate);
    }}
    styles={defaultStyles}
    firstDayOfWeek={1}
    minDate={tomorrow}
    timePicker={true}
    navigationPosition="around"
    locale={i18n.language}
/>